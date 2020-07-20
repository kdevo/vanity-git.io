#!/usr/bin/env python

import argparse
import time
import sys

import requests

parser = argparse.ArgumentParser(
    description="(￣ω￣; ) Vanity git.io shortener. Use with care & be fair.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "target",
    help="Target URL so that 'git.io/{code}' with '{code}' from file will redirect to target. "
    "If necessary, you can use the {code} placeholder which will be substituted (e.g. github.com?{code}). "
    "This trick allows the creation of multiple git.io links to the same page. "
    "Warning: If you abuse this functionality, the Octocat will be really mad at you.",
)
parser.add_argument(
    "--file",
    type=str,
    required=False,
    default="codes.txt",
    nargs=1,
    help="Path pointing to file that contains a list of custom codes. One per line.",
)
parser.add_argument(
    "--batch",
    action="store_true",
    help="Will attempt to create all URLs in the list (see 'file' param). "
    "Well. Not all - for fairness, the batch is limited to 5. Please also mind others!",
)
parser.add_argument(
    "--dry-run", action="store_true", help="Dry run will not create any URLs.",
)
parser.add_argument(
    "--print-urls", help="Print offending target URLs.", action="store_true",
)
args = parser.parse_args()


def last_resort(type, value, traceback):
    if type is KeyboardInterrupt:
        exit(0)
    else:
        print(f"{type}: {value}", file=sys.stderr)


sys.excepthook = last_resort
GIT_IO = "https://git.io"

old_print_len = 0
def printr(*msg, ret=True, **kwargs):
    global old_print_len
    if ret:
        msg_len = len(kwargs.get('sep', ' ').join(msg))
        print("\r", " " * abs(old_print_len - msg_len), end="", flush=True)
        print("\r", *msg, flush=True, **kwargs)
        old_print_len = msg_len
    else:
        print(*msg, **kwargs)
        old_print_len = 0


printr("Started vanity-git.io", ret=False)
if args.dry_run:
    printr("Warning: Dry-Run is active. Will not create any URLs.", ret=False)
    # Monkey-patch requests:
    def dry_post(**kwargs):
        response = requests.Response()
        response.status_code = 200
        return response

    requests.post = dry_post
printr("~", ret=False)


with open(args.file) as code_file:
    created_urls = 0
    for code in code_file:
        code = requests.utils.quote(code.strip())
        short_url = f"{GIT_IO}/{code}"
        printr(f"Trying {short_url} ...", end="")
        response = requests.get(url=short_url, allow_redirects=False)
        if response.status_code != 404:
            printr(
                f"( ╯﹏╰ ) URL {short_url} sold out.",
                f"Location: {response.headers.get('location', '<EMPTY>')}"
                if args.print_urls
                else "",
            )
            continue
        printr(f"(￣ω￣) URL {short_url} is available!")
        printr("Creating ...", end="")
        target = args.target.format(code=code)
        response = requests.post(url=GIT_IO, data={"code": code, "url": target},)
        if not response.ok:
            printr(f"Error: {response.text}")
            continue
        printr("Verifying ...", end="")
        response = requests.get(url=short_url)
        # The following check is necessary when e.g. using unicode chars as `code` for `target`.
        # Assume a unicode short url already exists. Then git.io falsely returns a status of 200,
        # even though `target` has already been shortened.
        if not args.dry_run and len(response.history) < 1:
            printr(f"Creation failed: The `target` seems to be shortened already.")
            printr(f"  Tip: Slightly obscure `target` (e.g. by appending a '/').")
            exit(int(response.status_code))
        printr(f"Successfully created {short_url} 🔗 {target}")
        created_urls += 1
        if not args.batch:
            exit(0)
        elif created_urls >= 5:
            printr(f"Creation limit exceeded.")
            exit(0)
        printr("", ret=False)
