import requests
import os
from bs4 import BeautifulSoup
from typing import Dict, Any, List

import google.generativeai as genai
# followers-> 2721

genai.configure(api_key=os.getenv("GOOGLE_GEMENI_API_KEY"))

DEVTO_API_URL = "https://dev.to"
DEV_TO_COOKIE = os.environ.get("DEV_TO_COOKIE")
DEV_TO_TOKEN = os.environ.get("DEV_TO_TOKEN")

ARTICLE_HEAD_SELECTOR = "crayons-article__header"
ARTICLE_BODY_SELECTOR = "crayons-article__main"

GEMINI_LLM = genai.GenerativeModel("gemini-1.5-flash-001")


class DevToCommenter:
    def __init__(self):
        self.api_url = DEVTO_API_URL
        self.auth_token = DEV_TO_TOKEN
        self.cookie = DEV_TO_COOKIE
        self.article_head_selector = ARTICLE_HEAD_SELECTOR
        self.article_body_selector = ARTICLE_BODY_SELECTOR
        self.llm = GEMINI_LLM

    def get_content(self, article_path: str) -> Dict[str, str]:
        try:
            response = requests.get(f"{self.api_url}/{article_path}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, features="html.parser")
            article_title = soup.find("header", class_=self.article_head_selector).text
            article_body = soup.find("div", class_=self.article_body_selector).text
            return {"article_title": article_title, "article_body": article_body}
        except requests.RequestException as e:
            print(f"Error fetching article content: {e}")
            return {}

    def get_my_feed(self) -> Dict[str, Any]:
        try:
            response = requests.get(
                f"{self.api_url}/search/feed_content?per_page=4&page=6&sort_by=hotness_score&sort_direction=desc&approved=&class_name=Article",
                headers={"cookie": self.cookie},
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching feed: {e}")
            return {}

    def post_comment(
        self, comment: str, article_id: int, article_path: str
    ) -> List[Dict[str, Any]]:
        headers = {
            "cookie": self.cookie,
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "origin": "https://dev.to",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": f"{self.api_url}/{article_path}",
            "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-csrf-token": "2N2VMreGpSd_h81JwgQnnTUuflQXpkvcEiGSnCUir61is8DTleA3T3SZ-ycj5qzv3q0VexsSL5qugCCxrC8uJA",
        }
        comment_body = {
            "comment": {
                "body_markdown": comment,
                "commentable_id": article_id,
                "commentable_type": "Article",
            }
        }
        like_body = {
            "reactable_type": "Article",
            "reactable_id": article_id,
            "category": "like",
            "authenticity_token": self.auth_token,
        }

        try:
            comment_response = requests.post(
                f"{self.api_url}/comments", json=comment_body, headers=headers
            )
            # comment_response.raise_for_status()
            like_response = requests.post(
                f"{self.api_url}/reactions", json=like_body, headers=headers
            )
            # like_response.raise_for_status()
            return [comment_response.json(), like_response.json()]
        except requests.RequestException as e:
            print(f"Error posting comment or like: {e}")
            return []

    def construct_prompt(self, article_title: str, article_content: str) -> str:
        return (
            f"Please generate a human-like comment for a blog post within 2 lines. "
            f"The comment should be relevant, thoughtful, and engaging. If you believe "
            f"there is nothing substantial to say about the content, return an empty string represented as <No/> \n"
            f"The blog title is {article_title}\n "
            f"<blog> {article_content}</blog>"
        )

    def main(self):
        myfeed = self.get_my_feed()
        if not myfeed:
            print("No feed data available.")
            return

        comments_added_articles = []
        for article in myfeed.get("result", []):
            article_path = article.get("path")
            article_title = article.get("title")
            article_id = article.get("id")
            article_content = self.get_content(article_path)

            if article_title and article_content:
                comment = self.llm.generate_content(
                    self.construct_prompt(
                        article_title, article_content.get("article_body", "")
                    )
                )
                print("comments", comment.text)
                if (
                    comment.text
                    and "<No/>" not in comment.text
                    and "<no/>" not in comment.text
                ):
                    self.post_comment(comment.text, article_id, article_path)
                    comments_added_articles.append(f"{DEVTO_API_URL}/{article_path}")

        print(comments_added_articles)


if __name__ == "__main__":
    commenter = DevToCommenter()
    commenter.main()
