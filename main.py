#!/usr/bin/env python

from typing import Iterator
from typing import Dict
from typing import List
from typing import Optional

import sys
import pprint
import sqlite3
import collections
import os
import glob
import re
import json
from datetime import datetime
from datetime import timedelta
import requests

BASE_URL = "https://api.helpscout.net/v2/"
APP_ID = os.environ["HELPSCOUT_APP_ID"]
APP_SECRET = os.environ["HELPSCOUT_APP_SECRET"]
FOLDER = "data"


def get_auth_token() -> str:
    now = datetime.now()
    expiration = None
    with open("auth.json") as f:
        payload = json.load(f)
        if "expiration" not in payload or now > datetime.fromisoformat(
            payload["expiration"]
        ):
            result = requests.post(
                "{}/oauth2/token".format(BASE_URL),
                data={
                    "grant_type": "client_credentials",
                    "client_id": APP_ID,
                    "client_secret": APP_SECRET,
                },
            )
            payload = result.json()
            expiration = now + timedelta(seconds=payload["expires_in"])
            payload["expiration"] = expiration.isoformat()

    with open("auth.json", "w") as f:
        json.dump(payload, f)

    return payload["access_token"]


def normalize_string(value: str) -> str:
    return re.sub("[^\w]+", "-", value)


class HelpScout:
    def __init__(self, token: str):
        self.token = token

    def download_all_data(self):
        endpoints = [
            "conversations",
            "customers",
            "mailboxes",
            "customer-properties",
            "tags",
            "teams",
            "users",
            "webhooks",
            "workflows",
        ]
        endpoints_to_skip = set()
        for endpoint in endpoints:
            if endpoint not in endpoints_to_skip:
                os.makedirs("{}/{}".format(FOLDER, endpoint), exist_ok=True)
                for url, payload in self.paginate_through_results_with_endpoint(
                    endpoint
                ):
                    filename = generate_filename(endpoint, url)
                    if os.path.exists(filename):
                        print("Skipping", filename)
                        break

                    print(url)
                    with open(filename, "w") as f:
                        json.dump(payload, f)

                files = glob.glob("{}/{}/*".format(FOLDER, endpoint))
                queue = collections.defaultdict(list)
                for file in files:
                    with open(file) as f:
                        payload = json.load(f)
                        for key in payload.get("_embedded", {}).keys():
                            items: List[Dict[str, dict]] = payload["_embedded"][key]
                            for item in items:
                                if "_links" in item:
                                    for k, v in item["_links"].items():
                                        if k != "self":
                                            queue[k].append(v["href"])

                for subendpoint, urls in queue.items():
                    os.makedirs(subendpoint, exist_ok=True)
                    for url in urls:
                        filename = generate_filename(subendpoint, url)
                        if os.path.exists(filename):
                            print("Skipping", filename)
                            continue

                        print(filename, url)
                        for _, payload in self.paginate_through_results(url):
                            with open(filename, "w") as f:
                                json.dump(payload, f)

    def paginate_through_results_with_endpoint(
        self, endpoint: str
    ) -> Iterator[tuple[str, dict]]:
        url = "{}{}".format(BASE_URL, endpoint)
        for result in self.paginate_through_results(url):
            yield result

    def paginate_through_results(
        self, url: Optional[str]
    ) -> Iterator[tuple[str, dict]]:
        while url is not None:
            response = requests.get(
                url=url,
                headers={"Authorization": "Bearer {}".format(self.token)},
            )
            try:
                payload = response.json()
            except:
                url = None
            else:
                yield url, payload
                if "next" in payload["_links"]:
                    url = payload["_links"]["next"]["href"]
                else:
                    url = None


def generate_filename(endpoint: str, url: str) -> str:
    return "{}/{}/{}.json".format(FOLDER, endpoint, normalize_string(url))


def get_customer_id(filename: str) -> Optional[str]:
    match = re.match(r".*-customers-(\d+)-.*", filename)
    if match:
        return match.group(1)

    return None


def generate_fields_for_tag(payload):
    return (
        payload["id"],
        payload["slug"],
        payload["name"],
        payload["color"],
        datetime.fromisoformat(payload["createdAt"][:-1]),
        payload["ticketCount"],
    )


def get_id(item, key):
    try:
        return item[key]["id"] if key in item else 0
    except:
        return item[key]


def generate_fields_for_thread(payload):
    return (
        payload["id"],
        payload["type"],
        payload.get("status"),
        payload.get("state"),
        json.dumps(payload["action"]),
        payload.get("body"),
        json.dumps(payload["source"]),
        get_id(payload, "customer"),
        get_id(payload, "createdBy"),
        get_id(payload, "assignedTo"),
        payload.get("savedReplyId"),
        ", ".join(payload["to"]),
        ", ".join(payload["cc"]),
        ", ".join(payload["bcc"]),
        datetime.fromisoformat(payload["createdAt"][:-1]),
    )


def generate_fields_for_conversation(payload):
    return (
        payload["id"],
        payload["number"],
        payload["threads"],
        payload["type"],
        payload["folderId"],
        payload["status"],
        payload["state"],
        payload["subject"],
        payload["preview"],
        payload["mailboxId"],
        get_id(payload, "assignee"),
        get_id(payload, "createdBy"),
        datetime.fromisoformat(payload["createdAt"][:-1]),
        get_id(payload, "closedBy"),
        get_id(payload, "closedByUser"),
        datetime.fromisoformat(payload["userUpdatedAt"][:-1]),
        datetime.fromisoformat(payload["customerWaitingSince"]["time"][:-1]),
        json.dumps(payload["source"]),
        json.dumps(payload["tags"]),
        ", ".join(payload["cc"]),
        ", ".join(payload["bcc"]),
        get_id(payload, "primaryCustomer"),
    )


def generate_fields_for_customer(payload):
    return (
        payload["id"],
        payload["firstName"],
        payload["lastName"],
        payload["gender"],
        payload["photoType"],
        payload["photoUrl"],
        datetime.fromisoformat(payload["createdAt"][:-1]),
        datetime.fromisoformat(payload["updatedAt"][:-1]),
    )


def generate_fields_for_website(
    payload: dict, filename: Optional[str], customer_id: Optional[str]
):
    if not customer_id and filename:
        customer_id = get_customer_id(filename)
        if not customer_id:
            return None

    return (payload["id"], payload["value"], customer_id)


def generate_fields_for_social_profile(
    payload: dict, filename: Optional[str], customer_id: Optional[str]
):
    if not customer_id and filename:
        customer_id = get_customer_id(filename)
        if not customer_id:
            return None

    return (payload["id"], payload["value"], payload["type"], customer_id)


def generate_fields_for_phone(
    payload: dict, filename: Optional[str], customer_id: Optional[str]
):
    if not customer_id and filename:
        customer_id = get_customer_id(filename)
        if not customer_id:
            return None

    return (payload["id"], payload["value"], payload["type"], customer_id)


def generate_fields_for_email(
    payload: dict, filename: Optional[str], customer_id: Optional[str]
):
    if not customer_id and filename:
        customer_id = get_customer_id(filename)
        if not customer_id:
            return None

    return (payload["id"], payload["value"], customer_id)


def generate_fields_for_address(payload: dict, filename: Optional[str]):
    if "city" not in payload:
        return None

    if filename:
        customer_id = get_customer_id(filename)
        if not customer_id:
            return None

    return (
        payload["city"],
        "\n".join(payload["lines"]),
        payload["state"],
        payload["postalCode"],
        payload["country"],
        customer_id,
    )


def generate_fields_for_user(payload: dict):
    if payload is None:
        return None

    return (
        payload["id"],
        payload["firstName"],
        payload["lastName"],
        payload["email"],
        payload["role"],
        payload["timezone"],
        payload["createdAt"],
        payload["updatedAt"],
        payload["type"],
        payload["mention"],
        payload["initials"],
        payload["jobTitle"],
        payload["phone"],
        ",".join(payload["alternateEmails"]),
    )


def generate_fields_for_mailbox(payload: dict):
    if payload is None:
        return None

    return (
        payload["id"],
        payload["name"],
        payload["slug"],
        payload["email"],
        datetime.fromisoformat(payload["createdAt"][:-1]),
        datetime.fromisoformat(payload["updatedAt"][:-1]),
    )


def generate_fields_for_chat(payload: dict):
    return (
        payload["id"],
        payload["value"],
        payload["type"],
    )


def generate_fields_for_workflow(payload: dict):
    if payload is None:
        return None

    return (
        payload["id"],
        payload["mailboxId"],
        payload["type"],
        payload["status"],
        payload["order"],
        payload["name"],
        datetime.fromisoformat(payload["createdAt"][:-1]),
        datetime.fromisoformat(payload["modifiedAt"][:-1]),
    )


embedded_data: dict = {
    "users": (
        "user",
        generate_fields_for_user,
        {},
    ),
    "threads": (
        "thread",
        generate_fields_for_thread,
        {},
    ),
    "conversations": (
        "conversation",
        generate_fields_for_conversation,
        {},
    ),
    "chats": (
        "chat",
        generate_fields_for_chat,
        {},
    ),
    "workflows": (
        "workflow",
        generate_fields_for_workflow,
        {},
    ),
    "tags": (
        "tag",
        generate_fields_for_tag,
        {},
    ),
    "mailboxes": (
        "mailbox",
        generate_fields_for_mailbox,
        {},
    ),
    "customers": (
        "customer",
        generate_fields_for_customer,
        {
            "emails": ("email", generate_fields_for_email),
            "phones": ("phone", generate_fields_for_phone),
            "social_profiles": (
                "social_profile",
                generate_fields_for_social_profile,
            ),
            "websites": ("website", generate_fields_for_website),
        },
    ),
}

if __name__ == "__main__":
    print(sys.argv)
    if sys.argv[1] == 'download':
        token = get_auth_token()
        hs = HelpScout(token)
        hs.download_all_data()
    elif sys.argv[1] == 'import':
        conn = sqlite3.connect("helpscout.db")
        with open("schema.sql") as f:
            with conn:
                conn.executescript(f.read())

        queue = []
        for filename in glob.glob("{}/*/*".format(FOLDER)):
            with open(filename) as f:
                payload = json.load(f)

                if payload is not None:
                    if "_embedded" in payload:
                        embedded = payload["_embedded"]

                        for name, (table, fun, linked_fields) in embedded_data.items():
                            for item in embedded.get(name, []):
                                queue.append((table, fun(item)))

                                for linked_field, (
                                    linked_table,
                                    linked_fun,
                                ) in linked_fields.items():
                                    for linked_item in item["_embedded"].get(
                                        linked_field, []
                                    ):
                                        queue.append(
                                            (
                                                linked_table,
                                                linked_fun(linked_item, None, item["id"]),
                                            )
                                        )

        for table, fields in queue:
            if not fields:
                continue

            with conn:
                conn.execute(
                    "INSERT OR IGNORE INTO {} VALUES ({})".format(
                        table, ", ".join(["?"] * len(fields))
                    ),
                    fields,
                )

        conn.close()
