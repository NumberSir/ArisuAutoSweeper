import time
from typing import Dict

from module.config.utils import *
from module.webui.fake import list_mod
from module.webui.setting import State

LANG = "zh-CN"
TRANSLATE_MODE = False


def set_language(s: str, refresh=False):
    global LANG
    LANG = next(
        (
            LANGUAGES[i]
            for i, lang in enumerate(LANGUAGES)
            if lang.lower() == s.lower()
        ),
        "en-US",
    )
    State.deploy_config.Language = LANG

    if refresh:
        from pywebio.session import run_js

        run_js("location.reload();")


def t(s, *args, **kwargs):
    """
    Get translation.
    other args, kwargs pass to .format()
    """
    return s if TRANSLATE_MODE else _t(s, LANG).format(*args, **kwargs)


def _t(s, lang=None):
    """
    Get translation, ignore TRANSLATE_MODE
    """
    if not lang:
        lang = LANG
    try:
        return dic_lang[lang][s]
    except KeyError:
        print(f"Language key ({s}) not found")
        return s


dic_lang: Dict[str, Dict[str, str]] = {}


def reload():
    for lang in LANGUAGES:
        if lang not in dic_lang:
            dic_lang[lang] = {}

        for mod_name, dir_name in list_mod():
            for path, v in deep_iter(read_file(filepath_i18n(lang, mod_name)), depth=3):
                dic_lang[lang][".".join(path)] = v

        for path, v in deep_iter(read_file(filepath_i18n(lang)), depth=3):
            dic_lang[lang][".".join(path)] = v

    for key in dic_lang["zh-CN"].keys():
        if dic_lang["zh-CN"][key] == key:
            dic_lang["zh-CN"][key] = dic_lang["en-US"][key]


def readable_time(before: str) -> str:
    """
    Convert "2023-08-29 12:30:53" to "3 Minutes Ago"
    """
    if not before:
        return t("Gui.Dashboard.NoData")
    try:
        ti = datetime.fromisoformat(before)
    except ValueError:
        return t("Gui.Dashboard.TimeError")
    if ti == DEFAULT_TIME:
        return t("Gui.Dashboard.NoData")

    diff = time.time() - ti.timestamp()
    if diff < -1:
        return t("Gui.Dashboard.TimeError")
    elif diff < 60:
        # < 1 min
        return t("Gui.Dashboard.JustNow")
    elif diff < 5400:
        # < 90 min
        return t("Gui.Dashboard.MinutesAgo", time=int(diff // 60))
    elif diff < 129600:
        # < 36 hours
        return t("Gui.Dashboard.HoursAgo", time=int(diff // 3600))
    elif diff < 1296000:
        # < 15 days
        return t("Gui.Dashboard.DaysAgo", time=int(diff // 86400))
    else:
        # >= 15 days
        return t("Gui.Dashboard.LongTimeAgo")
