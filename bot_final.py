import urllib.parse
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaVideo
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode
import httpx
from bs4 import BeautifulSoup
import re

# ---------------------------------------------------------
# إعدادات
# ---------------------------------------------------------
TOKEN = "8916943522:AAGMzK5IukewUnFVoagvQIigtaAHANkJ1vc"
BASE_URL = "https://www.xnxx-arabic.com"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# بيانات التصنيفات (من الصفحات السابقة)
# ---------------------------------------------------------
ORIENTATIONS = [
    ("سوي", "straight"),
    ("لواط", "gay"),
    ("شيميل", "shemale"),
]

STRAIGHT_CATS = [
    ("اختيار اليوم", "/todays-selection"),
    ("عائلة", "/search/familial_relations?id=91559326"),
    ("Hardcore", "/search/hardcore?top&id=92215726"),
    ("بزاز كبيرة", "/search/big_tits?id=64372255"),
    ("سكس", "/search/%D8%B3%D9%83%D8%B3?top&id=64009651"),
    ("18", "/search/teen?id=27154753"),
    ("Doggystyle", "/search/doggystyle?top&id=83286999"),
    ("الواقع الافتراضي", "/search/virtual_reality?id=84489299"),
    ("Natural tits", "/search/natural+tits?top&id=70995151"),
    ("عرب / عربي", "/search/arab?id=81361071"),
    ("Big dick", "/search/big+dick?top&id=22938513"),
    ("ميلف", "/search/milf?id=90636253"),
    ("Missionary", "/search/missionary?top&id=92140321"),
    ("لاتينية", "/search/latina?id=90641209"),
    ("Sex", "/search/sex?top&id=57763665"),
    ("ديوث/زوجة ساخنة", "/search/cuckold?id=91378153"),
    ("Deepthroat", "/search/deepthroat?top&id=47222467"),
    ("تمرين", "/search/workout?id=91792315"),
    ("Pussy licking", "/search/pussy+licking?top&id=86349045"),
    ("سيدات ناضجات", "/search/mature?id=83003091"),
    ("Hot", "/search/hot?top&id=79458977"),
    ("مؤخره كبيرة", "/search/big_ass?id=91915828"),
    ("Cowgirl", "/search/cowgirl?top&id=92116708"),
    ("تدليك", "/search/massage?id=89694061"),
    ("Orgasm", "/search/orgasm?top&id=91061227"),
    ("مذهل", "/search/exotic?id=81398665"),
    ("Xxx", "/search/xxx?top&id=90558637"),
    ("قذف داخلي", "/search/creampie?id=83862441"),
    ("Masturbation", "/search/masturbation?top&id=90723136"),
    ("قذف الأنثي", "/search/squirting?id=92225257"),
]

GAY_CATS = [
    ("اختيار اليوم", "/gay/todays-selection"),
    ("سكس", "/search/gay/%D8%B3%D9%83%D8%B3?top&id=60289923"),
    ("Sex", "/search/gay/sex?top&id=53330975"),
    ("Big dick", "/search/gay/big+dick?top&id=44566637"),
    ("سكس رجل مع رجل", "/search/gay/%D8%B3%D9%83%D8%B3+%D8%B1%D8%AC%D9%84+%D9%85%D8%B9+%D8%B1%D8%AC%D9%84?top&id=60289923"),
    ("سكس لواط", "/search/gay/%D8%B3%D9%83%D8%B3+%D9%84%D9%88%D8%A7%D8%B7?top&id=83102861"),
    ("Hardcore", "/search/gay/hardcore?top&id=81473185"),
    ("Masturbation", "/search/gay/masturbation?top&id=80177493"),
    ("Xxx com مترجم", "/search/gay/xxx+com+%D9%85%D8%AA%D8%B1%D8%AC%D9%85?top&id=85861177"),
    ("Femboy", "/search/gay/femboy?top&id=80744903"),
    ("Doggystyle", "/search/gay/doggystyle?top&id=88480796"),
    ("Fucking", "/search/gay/fucking?top&id=91540996"),
    ("Black cock", "/search/gay/black+cock?top&id=88546982"),
    ("Deepthroat", "/search/gay/deepthroat?top&id=49502535"),
    ("Handjob", "/search/gay/handjob?top&id=79272457"),
    ("Hot", "/search/gay/hot?top&id=74736745"),
]

SHEMALE_CATS = [
    ("سكس", "/search/shemale/%D8%B3%D9%83%D8%B3?top&id=77254697"),
    ("Xxx com مترجم", "/search/shemale/xxx+com+%D9%85%D8%AA%D8%B1%D8%AC%D9%85?top&id=74886788"),
    ("Guy fucks", "/search/shemale/guy+fucks?top&id=68860701"),
    ("Hardcore", "/search/shemale/hardcore?top&id=91093264"),
    ("Deepthroat", "/search/shemale/deepthroat?top&id=88389020"),
    ("Sex", "/search/shemale/sex?top&id=90145975"),
    ("Super hot", "/search/shemale/super+hot?top&id=65651829"),
    ("Tranny sex", "/search/shemale/tranny+sex?top&id=57515753"),
    ("Hot tranny blowjob", "/search/shemale/hot+tranny+blowjob?top&id=80409119"),
    ("سكس مصري جديد", "/search/shemale/%D8%B3%D9%83%D8%B3+%D9%85%D8%B5%D8%B1%D9%8A+%D8%AC%D8%AF%D9%8A%D8%AF?top&id=23698476"),
    ("Transgender", "/search/shemale/transgender?top&id=86014279"),
    ("Fucks girl", "/search/shemale/fucks+girl?top&id=68713245"),
    ("Fuck girl", "/search/shemale/fuck+girl?top&id=73702641"),
    ("Hot  big cock", "/search/shemale/hot++big+cock?top&id=86743861"),
    ("Free tranny porn videos", "/search/shemale/free+tranny+porn+videos?top&id=87905627"),
    ("Guy fuck", "/search/shemale/guy+fuck?top&id=88884112"),
    ("Masturbation", "/search/shemale/masturbation?top&id=83878093"),
    ("Big dick", "/search/shemale/big+dick?top&id=90204412"),
    ("Hot  sex", "/search/shemale/hot++sex?top&id=78684783"),
    ("Hot  fucks girl", "/search/shemale/hot++fucks+girl?top&id=85053661"),
    ("سكس شيميل", "/search/shemale/%D8%B3%D9%83%D8%B3+%D8%B4%D9%8A%D9%85%D9%8A%D9%84?top&id=24739329"),
    ("Doggystyle", "/search/shemale/doggystyle?top&id=69044157"),
    ("Xxx", "/search/shemale/xxx?top&id=74532171"),
    ("Hot tranny fucks girl", "/search/shemale/hot+tranny+fucks+girl?top&id=84851205"),
    ("Guy on", "/search/shemale/guy+on?top&id=85414453"),
    ("Fucks guy", "/search/shemale/fucks+guy?top&id=91203628"),
    ("Hot tranny anal", "/search/shemale/hot+tranny+anal?top&id=88648454"),
    ("Feminine trans", "/search/shemale/feminine+trans?top&id=82289733"),
    ("Transsexual women", "/search/shemale/transsexual+women?top&id=81625449"),
]

CATS_BY_ORIENTATION = {
    "straight": STRAIGHT_CATS,
    "gay": GAY_CATS,
    "shemale": SHEMALE_CATS,
}

ITEMS_PER_PAGE = 8   # عدد الأزرار في الصفحة الواحدة

# ---------------------------------------------------------
# دوال مساعدة
# ---------------------------------------------------------
def get_user_state(context: ContextTypes.DEFAULT_TYPE) -> dict:
    if "state" not in context.user_data:
        context.user_data["state"] = {
            "orientation": None,
            "category_path": None,
            "category_name": None,
            "cat_page": 0,
            "vid_page": 0,
        }
    return context.user_data["state"]


async def fetch_videos(category_path: str, page: int = 0) -> list:
    """يحاول جلب قائمة الفيديوهات من صفحة التصنيف"""
    url = BASE_URL + category_path
    if page > 0:
        # معظم صفحات xnxx تستخدم /page أو ?p=
        if "?" in category_path:
            url += f"&p={page}"
        else:
            url += f"/page/{page + 1}" if not category_path.endswith("/") else f"page/{page + 1}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ar,en;q=0.9",
    }
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        logger.error(f"Fetch error: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    videos = []
    for block in soup.select("div.thumb-block:not(.thumb-ad)"):
        a = block.select_one("div.thumb-under p a") or block.select_one('a[href*="/video-"]')
        if not a:
            continue
        href = a.get("href", "")
        title = (a.get("title") or a.get_text(strip=True)).strip()
        img = block.select_one("img")
        thumb = None
        preview = None
        if img:
            thumb = img.get("src") or img.get("data-src")
            preview = img.get("data-pvv")
        if not preview:
            thumb_div = block.select_one("div.thumb img")
            if thumb_div:
                preview = thumb_div.get("data-pvv")
        meta = block.select_one("p.metadata")
        duration = ""
        views = ""
        if meta:
            text = meta.get_text(" ", strip=True)
            m = re.search(r"(\d+\s*min|\d+\s*sec)", text, re.I)
            if m:
                duration = m.group(1).replace(" ", "")
            m2 = re.search(r"([\d.,]+[kKmM]?)\s*", text)
            if m2:
                views = m2.group(1)
        if href and "/video-" in href and title:
            videos.append({
                "title": title[:140],
                "path": href,
                "thumb": thumb,
                "preview": preview,
                "duration": duration,
                "views": views,
            })
        if len(videos) >= 20:
            break
    return videos


# ---------------------------------------------------------
# القائمة الرئيسية
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = get_user_state(context)
    state["orientation"] = None
    state["category_path"] = None
    state["cat_page"] = 0
    state["vid_page"] = 0

    keyboard = [
        [InlineKeyboardButton("🏷️ اختر التصنيف", callback_data="show_orientations")],
        [InlineKeyboardButton("🔍 بحث بالكلمة", callback_data="search_info")],
        [InlineKeyboardButton("🗑️ مسح الإعدادات", callback_data="reset_state")],
    ]
    text = (
        "مرحباً بك 👋\n\n"
        "اختر التصنيف الرئيسي ثم الفرعي، وبعدها ستظهر لك الفيديوهات داخل البوت.\n"
        "عند اختيار فيديو سيصلك معاينة قصيرة + زر للمشاهدة الفورية."
    )
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# ---------------------------------------------------------
# معالجة الأزرار
# ---------------------------------------------------------
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    state = get_user_state(context)

    # ----- القائمة الرئيسية -----
    if data == "main_menu" or data == "reset_state":
        await start(update, context)
        return

    # ----- اختيار التوجه -----
    if data == "show_orientations":
        keyboard = [[InlineKeyboardButton(name, callback_data=f"orient_{key}")] for name, key in ORIENTATIONS]
        keyboard.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")])
        await query.edit_message_text("🏷️ **اختر التصنيف الرئيسي:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
        return

    if data.startswith("orient_"):
        orient_key = data.replace("orient_", "")
        state["orientation"] = orient_key
        state["cat_page"] = 0
        await show_categories(query, context)
        return

    # ----- تصفح التصنيفات الفرعية -----
    if data == "cats_prev":
        state["cat_page"] = max(0, state["cat_page"] - 1)
        await show_categories(query, context)
        return
    if data == "cats_next":
        state["cat_page"] += 1
        await show_categories(query, context)
        return
    if data == "back_orientations":
        state["orientation"] = None
        await handle_callback(update, context)  # will hit show_orientations if we set data, but simpler:
        keyboard = [[InlineKeyboardButton(name, callback_data=f"orient_{key}")] for name, key in ORIENTATIONS]
        keyboard.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")])
        await query.edit_message_text("🏷️ **اختر التصنيف الرئيسي:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
        return

    if data.startswith("cat_"):
        # cat_<index>
        try:
            idx = int(data.split("_")[1])
            cats = CATS_BY_ORIENTATION.get(state["orientation"], [])
            if 0 <= idx < len(cats):
                name, path = cats[idx]
                state["category_name"] = name
                state["category_path"] = path
                state["vid_page"] = 0
                await show_videos(query, context)
        except Exception as e:
            logger.error(e)
            await query.edit_message_text("حدث خطأ، حاول مرة أخرى.")
        return

    # ----- تصفح الفيديوهات -----
    if data == "vids_prev":
        state["vid_page"] = max(0, state["vid_page"] - 1)
        await show_videos(query, context)
        return
    if data == "vids_next":
        state["vid_page"] += 1
        await show_videos(query, context)
        return
    if data == "back_cats":
        await show_categories(query, context)
        return

    if data.startswith("vid_"):
        # vid_<index_in_current_page>
        try:
            idx = int(data.split("_")[1])
            videos = context.user_data.get("current_videos", [])
            if 0 <= idx < len(videos):
                video = videos[idx]
                await send_video_card(query, context, video)
        except Exception as e:
            logger.error(e)
            await query.answer("خطأ في اختيار الفيديو", show_alert=True)
        return

    if data == "search_info":
        await query.edit_message_text(
            "🔎 **البحث:**\n\nأرسل كلمة البحث مباشرة في رسالة نصية، وسأعرض لك النتائج.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return


async def show_categories(query, context):
    state = get_user_state(context)
    orient = state["orientation"]
    cats = CATS_BY_ORIENTATION.get(orient, [])
    page = state["cat_page"]
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_cats = cats[start:end]

    orient_name = next((n for n, k in ORIENTATIONS if k == orient), orient)

    keyboard = []
    for i, (name, path) in enumerate(page_cats):
        global_idx = start + i
        btn_text = name if len(name) <= 30 else name[:27] + "..."
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"cat_{global_idx}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ السابق", callback_data="cats_prev"))
    if end < len(cats):
        nav.append(InlineKeyboardButton("التالي ➡️", callback_data="cats_next"))
    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton("🔙 التصنيفات الرئيسية", callback_data="back_orientations")])
    keyboard.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")])

    text = f"🏷️ **تصنيفات ({orient_name})** — صفحة {page + 1}"
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def show_videos(query, context):
    state = get_user_state(context)
    path = state["category_path"]
    name = state["category_name"]
    page = state["vid_page"]

    await query.edit_message_text(f"⏳ جاري جلب فيديوهات **{name}** ...", parse_mode=ParseMode.MARKDOWN)

    videos = await fetch_videos(path, page)
    context.user_data["current_videos"] = videos

    if not videos:
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للتصنيفات", callback_data="back_cats")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            f"لم أتمكن من جلب فيديوهات من «{name}».\nجرب تصنيفاً آخر أو أعد المحاولة لاحقاً.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    keyboard = []
    for i, v in enumerate(videos[:ITEMS_PER_PAGE]):
        title = v["title"]
        if len(title) > 35:
            title = title[:32] + "..."
        dur = f" ({v['duration']})" if v["duration"] else ""
        keyboard.append([InlineKeyboardButton(f"{title}{dur}", callback_data=f"vid_{i}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ السابق", callback_data="vids_prev"))
    # نفترض أن هناك المزيد إذا رجعنا 20 فيديو
    if len(videos) >= 15:
        nav.append(InlineKeyboardButton("التالي ➡️", callback_data="vids_next"))
    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton("🔙 التصنيفات", callback_data="back_cats")])
    keyboard.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")])

    text = f"🎬 **{name}** — صفحة {page + 1}\nاختر فيديو لعرض المعاينة:"
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def send_video_card(query, context, video: dict):
    """يرسل بطاقة أنيقة: معاينة قصيرة + عنوان + زر مشاهدة فورية"""
    full_url = BASE_URL + video["path"]
    caption = f"🎬 **{video['title']}**\n"
    if video["duration"]:
        caption += f"⏱ المدة: {video['duration']}\n"
    if video["views"]:
        caption += f"👁 المشاهدات: {video['views']}\n"
    caption += "\nاضغط الزر بالأسفل للمشاهدة الكاملة."

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ اضغط للمشاهدة الفورية", url=full_url)],
        [InlineKeyboardButton("🔙 العودة للقائمة", callback_data="back_cats")],
    ])

    # محاولة إرسال المعاينة كفيديو
    preview_url = video.get("preview")
    if preview_url:
        try:
            await query.message.reply_video(
                video=preview_url,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
                supports_streaming=True,
            )
            await query.answer()
            return
        except Exception as e:
            logger.warning(f"Failed to send preview video: {e}")

    # fallback: صورة مصغرة
    thumb = video.get("thumb")
    if thumb:
        try:
            await query.message.reply_photo(
                photo=thumb,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
            )
            await query.answer()
            return
        except Exception as e:
            logger.warning(f"Failed to send thumb: {e}")

    # آخر حل: رسالة نصية فقط
    await query.message.reply_text(caption, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
    await query.answer()


# ---------------------------------------------------------
# البحث النصي
# ---------------------------------------------------------
async def handle_search_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    search_term = update.message.text.strip()
    if not search_term:
        return

    encoded = urllib.parse.quote(search_term)
    # نستخدم بحث عادي
    path = f"/search/{encoded}"
    state = get_user_state(context)
    state["category_name"] = f"بحث: {search_term}"
    state["category_path"] = path
    state["vid_page"] = 0

    # نرسل رسالة مؤقتة ثم نجلب
    msg = await update.message.reply_text(f"⏳ جاري البحث عن **{search_term}** ...", parse_mode=ParseMode.MARKDOWN)

    videos = await fetch_videos(path, 0)
    context.user_data["current_videos"] = videos

    if not videos:
        await msg.edit_text("لم أجد نتائج. جرب كلمة أخرى.")
        return

    keyboard = []
    for i, v in enumerate(videos[:ITEMS_PER_PAGE]):
        title = v["title"]
        if len(title) > 35:
            title = title[:32] + "..."
        dur = f" ({v['duration']})" if v["duration"] else ""
        keyboard.append([InlineKeyboardButton(f"{title}{dur}", callback_data=f"vid_{i}")])

    keyboard.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")])

    await msg.edit_text(
        f"🔍 نتائج البحث عن **{search_term}**:\nاختر فيديو:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_query))
    print("البوت يعمل الآن...")
    app.run_polling()


if __name__ == "__main__":
    main()
