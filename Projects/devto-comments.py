import requests
import os
from bs4 import BeautifulSoup
from typing import Dict, Any, List

import google.generativeai as genai
from typing import Optional

# followers-> 2721

genai.configure(api_key=os.getenv("GOOGLE_GEMENI_API_KEY"))


class Author:
    id: str
    name: str
    image: str
    username: str
    permalink: str


class Source:
    id: str
    handle: str
    name: str
    permalink: str
    image: str
    type: str


class UserState:
    vote: int
    flags: Dict[str, Optional[Any]]


class Node:
    id: str
    title: str
    image: str
    readTime: int
    permalink: str
    commentsPermalink: str
    createdAt: str
    commented: bool
    bookmarked: bool
    views: Optional[int]
    numUpvotes: int
    numComments: int
    summary: str
    bookmark: Optional[Any]
    author: Author
    type: str
    tags: List[str]
    source: Source
    userState: UserState
    slug: str
    sharedPost: Optional[Any]
    trending: Optional[Any]
    feedMeta: Optional[Any]
    collectionSources: List[Any]
    numCollectionSources: int
    updatedAt: str
    pinnedAt: Optional[Any]
    contentHtml: str
    read: bool
    upvoted: bool
    downvoted: bool


DEVTO_API_URL = "https://dev.to"
DEV_TO_COOKIE = os.environ.get("DEV_TO_COOKIE")
DEV_TO_TOKEN = os.environ.get("DEV_TO_TOKEN")

ARTICLE_HEAD_SELECTOR = "crayons-article__header"
ARTICLE_BODY_SELECTOR = "crayons-article__main"

DAILY_DEV_API_URL = "https://api.daily.dev/graphql"
DAILY_DEV_COOKIE = os.environ.get(
    "DAILY_DEV_COOKIESS",
)


GEMINI_LLM = genai.GenerativeModel("gemini-1.5-flash-001")


class DevToCommenter:
    def __init__(self, page=1):
        self.api_url = DEVTO_API_URL
        self.auth_token = DEV_TO_TOKEN
        self.cookie = DEV_TO_COOKIE
        self.article_head_selector = ARTICLE_HEAD_SELECTOR
        self.article_body_selector = ARTICLE_BODY_SELECTOR
        self.llm = GEMINI_LLM
        self.page = page

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
                f"{self.api_url}/search/feed_content?per_page=10&page={self.page}&sort_by=hotness_score&sort_direction=desc&approved=&class_name=Article",
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

        print("TOTAL POST", len(myfeed.get("result")))

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
                print(comment.text, "\n", f"{DEVTO_API_URL}/{article_path}", "\n")
                if (
                    comment.text
                    and "<No/>" not in comment.text
                    and "<no/>" not in comment.text
                ):
                    user_input = input(
                        f"Do you want to post this comment for the post titled '{article_title}'? (yes/no): "
                    )
                    if user_input.lower() == "yes":
                        self.post_comment(comment.text, article_id, article_path)
                        comments_added_articles.append(
                            f"{DEVTO_API_URL}/{article_path}"
                        )

        # print(comments_added_articles)


class DailyDev:
    def __init__(self):
        self.api_url = DAILY_DEV_API_URL
        self.cookie = DAILY_DEV_COOKIE
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
            body = {
                "query": '\n  query Feed(\n    $loggedIn: Boolean! = false\n    $first: Int\n    $after: String\n    $ranking: Ranking\n    $version: Int\n    $supportedTypes: [String!] = ["article","share","freeform","video:youtube","collection"]\n  ) {\n    page: feed(\n      first: $first\n      after: $after\n      ranking: $ranking\n      version: $version\n      supportedTypes: $supportedTypes\n    ) {\n      ...FeedPostConnection\n    }\n  }\n  \n  fragment FeedPostConnection on PostConnection {\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n    edges {\n      node {\n        ...FeedPost\n        contentHtml\n        ...UserPost @include(if: $loggedIn)\n      }\n    }\n  }\n  \n  fragment FeedPost on Post {\n    ...FeedPostInfo\n    sharedPost {\n      id\n      title\n      image\n      readTime\n      permalink\n      commentsPermalink\n      createdAt\n      type\n      tags\n      source {\n        id\n        handle\n        permalink\n        image\n      }\n      slug\n    }\n    trending\n    feedMeta\n    collectionSources {\n      handle\n      image\n    }\n    numCollectionSources\n    updatedAt\n    slug\n  }\n  \n  fragment FeedPostInfo on Post {\n    id\n    title\n    image\n    readTime\n    permalink\n    commentsPermalink\n    createdAt\n    commented\n    bookmarked\n    views\n    numUpvotes\n    numComments\n    summary\n    bookmark {\n      remindAt\n    }\n    author {\n      id\n      name\n      image\n      username\n      permalink\n    }\n    type\n    tags\n    source {\n      id\n      handle\n      name\n      permalink\n      image\n      type\n    }\n    userState {\n      vote\n      flags {\n        feedbackDismiss\n      }\n    }\n    slug\n  }\n\n  \n  fragment UserPost on Post {\n    read\n    upvoted\n    commented\n    bookmarked\n    downvoted\n  }\n\n\n',
                "variables": {
                    "version": 47,
                    "ranking": "POPULARITY",
                    "first": 500,
                    "loggedIn": True,
                },
            }

            response = requests.post(
                f"{self.api_url}",
                json=body,
                headers={
                    "cookie": self.cookie,
                    "origin": "chrome-extension://jlmpjdjjbgclbocgajdjefcidcncaied",
                    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                },
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching feed: {e}")
            return {}

    def post_comment(self, comment: str, articel_id: str) -> List[Dict[str, Any]]:
        headers = {
            "cookie": self.cookie,
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "origin": self.api_url,
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": self.api_url,
            "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-csrf-token": "2N2VMreGpSd_h81JwgQnnTUuflQXpkvcEiGSnCUir61is8DTleA3T3SZ-ycj5qzv3q0VexsSL5qugCCxrC8uJA",
        }
        comment_body = {
            "query": "\n  mutation COMMENT_ON_POST_MUTATION($id: ID!, $content: String!) {\n    comment: commentOnPost(postId: $id, content: $content) {\n      ...CommentFragment\n    }\n  }\n  \n  fragment CommentFragment on Comment {\n    id\n    contentHtml\n    createdAt\n    lastUpdatedAt\n    permalink\n    numUpvotes\n    author {\n      ...UserAuthor\n    }\n    userState {\n      vote\n    }\n  }\n  \n  fragment UserAuthor on User {\n    ...UserShortInfo\n    contentPreference {\n      ...ContentPreferenceFragment\n    }\n  }\n  \n  fragment ContentPreferenceFragment on ContentPreference {\n    referenceId\n    type\n    status\n  }\n\n  \n  fragment UserShortInfo on User {\n    id\n    name\n    image\n    permalink\n    username\n    bio\n    createdAt\n    reputation\n    companies {\n      name\n      image\n    }\n  }\n\n\n\n",
            "variables": {"content": comment, "id": articel_id},
        }

        try:
            comment_response = requests.post(
                f"{self.api_url}", json=comment_body, headers=headers
            ).json()

            if comment_response and "erros" in comment_response:
                print("error posting comments", comment_response["erros"])
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
        # print(self.post_comment(":)", "iQ3YtojCI"))
        # return
        # print(myfeed)
        if not myfeed or (not myfeed["data"]):
            print("No feed data available.", myfeed)
            return

        comments_added_articles = []
        print("Total post fetechd count", len(myfeed["data"]["page"]["edges"]))
        for node in myfeed["data"]["page"]["edges"]:
            # post posed on daily dev itself
            node: Node = node["node"]
            if (
                node
                and "contentHtml" in node
                and "title" in node
                and node["contentHtml"]
                and node["title"]
            ):
                comment = self.llm.generate_content(
                    self.construct_prompt(node["title"], node["contentHtml"])
                )
                if (
                    comment.text
                    and "<No/>" not in comment.text
                    and "<no/>" not in comment.text
                ):
                    print(
                        comment.text,
                        f"https://app.daily.dev/posts/{node['slug']}\n",
                    )
                    user_input = input(
                        f"Do you want to post this comment for the post titled '{node['title']}'? (yes/no): "
                    )
                    if user_input.lower() == "yes":
                        print(self.post_comment(comment.text, node["id"]), "\n")

                        comments_added_articles.append(
                            f"https://app.daily.dev/posts/{node['slug']}"
                        )


if __name__ == "__main__":
    commenter = DailyDev()
    # commenter = DevToCommenter()
    commenter.main()
