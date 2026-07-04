import os
import sys

from config.paths import PROJECT_ROOT


def configure_project_root():
    sys.path.insert(0, str(PROJECT_ROOT))
    os.chdir(PROJECT_ROOT)


def configure_wechat_proxy_bypass():
    wechat_no_proxy = "qq.com,weixin.qq.com,wechat.com,wx.qq.com,wx2.qq.com,webpush.wx2.qq.com,login.weixin.qq.com"
    current_no_proxy = os.environ.get("NO_PROXY") or os.environ.get("no_proxy")
    if current_no_proxy:
        os.environ["NO_PROXY"] = f"{current_no_proxy},{wechat_no_proxy}"
    else:
        os.environ["NO_PROXY"] = wechat_no_proxy
    os.environ["no_proxy"] = os.environ["NO_PROXY"]


def ensure_runtime_paths():
    config_file = PROJECT_ROOT / "config" / "config.yaml"
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在：{config_file}")

    for path in [PROJECT_ROOT / "logs", PROJECT_ROOT / "data"]:
        path.mkdir(parents=True, exist_ok=True)


def main():
    configure_project_root()
    configure_wechat_proxy_bypass()
    ensure_runtime_paths()

    import wxbot

    wxbot.main()


if __name__ == "__main__":
    main()
