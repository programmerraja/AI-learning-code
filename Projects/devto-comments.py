import requests
import os
from bs4 import BeautifulSoup
from typing import Dict, Any, List

import google.generativeai as genai
from typing import Optional
from dotenv import load_dotenv

load_dotenv("../.env")
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
DEV_TO_COOKIE = os.environ.get("DEV_TO_COOKIE","GA1.1.1019330267.1713703994; client_id=TG3c3opeZHa9z.9a929f86-a70c-431d-9215-8b0581d51466; user_experience_level=5; remember_user_token=eyJfcmFpbHMiOnsibWVzc2FnZSI6IlcxczBNekE1TVROZExDSjRhbnBIUW5oVVJUUlFORUoxTlcxNVUyMUJhU0lzSWpFM05UWXlOelF4TnpFdU9UQXdOalEwTlNKZCIsImV4cCI6IjIwMjYtMDItMjVUMDU6NTY6MTEuOTAwWiIsInB1ciI6ImNvb2tpZS5yZW1lbWJlcl91c2VyX3Rva2VuIn19--ce65768d4e26eed6738634f7352b3431577af18d; _Devto_Forem_Session=5ed6ab4845001d9dbeb41a46dc9f6490; ahoy_visitor=45f80380-095c-4dd5-b86b-e6ea051095eb; ahoy_visit=743d0ebc-e948-422a-b797-9feee7bd4154; _ga_TYEM8Y3JN3=GS2.1.s1758499630$o841$g1$t1758500630$j12$l0$h0")
DEV_TO_TOKEN = os.environ.get("DEV_TO_TOKEN","Wp-RNWMfFgi7FCz6plLMTbdqn-GEjXCAzAlPTjTgJx3CuiN7PXXUx2a1Fv2XcjRw_4IediPMEdCmZuYoP2FNRA")

ARTICLE_HEAD_SELECTOR = "crayons-article__header"
ARTICLE_BODY_SELECTOR = "crayons-article__main"

DAILY_DEV_API_URL = "https://api.daily.dev/graphql"
DAILY_DEV_COOKIE = os.environ.get("DAILY_DEV_COOKIESS","da2=NbQgWXH9JdceQ4lfD3WCY; _tracking_consent=%7B%22con%22%3A%7B%22CMP%22%3A%7B%22a%22%3A%22%22%2C%22m%22%3A%22%22%2C%22p%22%3A%22%22%2C%22s%22%3A%22%22%7D%7D%2C%22v%22%3A%222.1%22%2C%22region%22%3A%22INTN%22%2C%22reg%22%3A%22%22%2C%22purposes%22%3A%7B%22a%22%3Atrue%2C%22p%22%3Atrue%2C%22m%22%3Atrue%2C%22t%22%3Atrue%7D%2C%22display_banner%22%3Afalse%2C%22sale_of_data_region%22%3Afalse%7D; _shopify_y=b3a911c2-9625-40e0-be16-9ba67e8d506f; _ga=GA1.1.840969628.1722752906; _ga_Y94RMTGW0M=GS1.1.1732963253.7.0.1732963254.0.0.0; das=e5fa3ec3-3355-49ad-8842-54c05ece3fbe; _tt_enable_cookie=1; _ttp=01K0DK9WC6B44M6YXWAQ1EZR2X_.tt.1; ilikecookies=true; ory_kratos_session=MTc1Nzg5OTcwNHw5OUhXdGF1c2sxcDRheUdldWRKaW84c3pTR1RnVFlNLUNFREdsN3ZxTy03TV82ZUlHOGVLRHV0cm1uUWo5NnM0UFIxQ0dyRlZnLVR6UV9Sc3JncG9NOFVxTHk4NWJXUG8walpfbHhTWnhGZTN5b05LMlJYZGxMUTVSck9NM0tpT1Rvbk9MUzdyVkJfc1JJVURuem5PTS1XWU9IaWlkQTc3TWxlSGRyWGsweGc5QjlKYWFEbmJ6V2t2dk9GRENKdjdtTmRUcnoza21xNzhGdjJTWFl5b255Ul9UdTljRGZyTWZJNjREUGZ4b3hPaWRTbElVQUtCamk0MGc0Y3phdnU1MWprcFVYbnJMMjkxVEVpbXw5e4m4dioKOTnb4tZ1u6hjYjl9B0lSYcHmQ9EIGeLHTQ==; _rdt_uuid=1752803109031.7c49e1c8-c080-41ea-80c9-c5cb600f2db9; ttcsid=1758063330491::b2i_bCKd60nAeGMl85tI.2.1758063357432.0; ttcsid_CO2RCPBC77U37LT1TAIG=1758063330491::qabt9Cpk4LcPFUw9QSWT.2.1758063357749.0; _ga_VTGLXD7QSN=GS2.1.s1758063328$o2$g1$t1758063364$j24$l0$h0; da3=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTg1MDEwMjQuODgxLCJ1c2VySWQiOiJOYlFnV1hIOUpkY2VRNGxmRDNXQ1kiLCJyb2xlcyI6W10sImlzVGVhbU1lbWJlciI6ZmFsc2UsImlzUGx1cyI6ZmFsc2UsImlhdCI6MTc1ODUwMDEyNCwiYXVkIjoiRGFpbHkiLCJpc3MiOiJEYWlseSBBUEkifQ.tO-Vuo4YroeJ3l2NJxKiRysmm5j-TaAw_jb-BmVgjsblKjaTUwF8JXkIqn5ePIemCifCHl4X-Ue6nsDeSS27iNpp8_Tl_N8jld8kcBFtItOrjKIvYUHAtNdAjWQNopAd7NGlRfFh0gygUw0Nv4ZxRFBHnYeS9ZKvWjlZu3sIz7iojMJVP5J-yDSUHJ70ICdE_CNuSlBfrYigMhqV8925eROtetSpEYXxGJcMouTWFu1uTvBXgVkGhvUvb5uLwL-4w54k18yIDxe-2Mow4EN2N4TciDuvPRfRMz_N_T44cwrB_GYaz_IbGTvpxYtnk7fkrXceGhVGoJoc5urSb3R5YQ.MiidBW00cWLWGn0FUuMGkTH4gqkE5rPSbjzAdvvupMU")


GEMINI_LLM = genai.GenerativeModel("models/gemini-1.5-flash")


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
                "body_markdown": comment.strip(),
                "commentable_id": str(article_id),
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
            print(comment_body)
            comment_response = requests.post(
                f"{self.api_url}/comments", json=comment_body, headers=headers
            )
            # comment_response.raise_for_status()
            like_response = requests.post(
                f"{self.api_url}/reactions", json=like_body, headers=headers
            )
            # like_response.raise_for_status()
            return []
        except requests.RequestException as e:
            print(f"Error posting comment or like: {e}")
            return []

    def construct_prompt(self, article_title: str, article_content: str) -> str:
        return f"""
            (C) Context: You are asked to create a brief, relevant comment for a blog post. The comment should reflect a professional yet casual tone typical of an Indian software developer. It should not invite further discussion but still acknowledge the content in a thoughtful manner.
            (O) Objective: Generate a short, insightful, and relevant two-line comment. If the content is insufficient to generate a meaningful response, return an empty string as <No/>.
            (S) Style: The comment should be straightforward, clear, and to the point, with a tone that's polite and professional, but not overly formal.
            (T) Tone: The tone should be neutral and professional, with a touch of casualness typical of a software developer from India—concise and focused on the content, without being overly elaborate or encouraging further conversation.
            (A) Audience: The comment is for a general online audience, with an emphasis on people familiar with technical topics or a professional software development context.
            (R) Response: A concise, relevant two-line comment or an empty string if the content lacks substance for a meaningful response.
            The blog title is {article_title}, and here is the article content: <blog> {article_content}</blog>"""

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

    def get_my_feed(self, after) -> Dict[str, Any]:
        try:
            most_popular_query = {
                "query": '\n  query MostDiscussedFeed(\n    $loggedIn: Boolean! = false\n    $first: Int\n    $after: String\n    $period: Int\n    $supportedTypes: [String!] = ["article","share","freeform","video:youtube","collection"]\n    $source: ID\n    $tag: String\n  ) {\n    page: mostDiscussedFeed(first: $first, after: $after, period: $period, supportedTypes: $supportedTypes, source: $source, tag: $tag) {\n      ...FeedPostConnection\n    }\n  }\n  \n  fragment FeedPostConnection on PostConnection {\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n    edges {\n      node {\n        ...FeedPost\n        contentHtml\n        ...UserPost @include(if: $loggedIn)\n      }\n    }\n  }\n  \n  fragment FeedPost on Post {\n    ...FeedPostInfo\n    sharedPost {\n      id\n      title\n      image\n      readTime\n      permalink\n      commentsPermalink\n      createdAt\n      type\n      tags\n      private\n      source {\n        id\n        handle\n        permalink\n        image\n        type\n      }\n      slug\n      clickbaitTitleDetected\n      translation {\n        ...PostTranslateableFields\n      }\n    }\n    trending\n    feedMeta\n    collectionSources {\n      handle\n      image\n    }\n    numCollectionSources\n    updatedAt\n    slug\n  }\n  \n  fragment FeedPostInfo on Post {\n    id\n    title\n    image\n    readTime\n    permalink\n    commentsPermalink\n    createdAt\n    commented\n    bookmarked\n    views\n    numUpvotes\n    numComments\n    numAwards\n    summary\n    bookmark {\n      remindAt\n    }\n    author {\n      id\n      name\n      image\n      username\n      permalink\n      contentPreference {\n        status\n      }\n    }\n    type\n    tags\n    source {\n      id\n      handle\n      name\n      permalink\n      image\n      type\n      currentMember {\n        flags {\n          collapsePinnedPosts\n        }\n      }\n    }\n    userState {\n      vote\n      flags {\n        feedbackDismiss\n      }\n      awarded\n    }\n    slug\n    clickbaitTitleDetected\n    language\n    translation {\n      ...PostTranslateableFields\n    }\n  }\n  \n  fragment PostTranslateableFields on PostTranslation {\n    title\n    titleHtml\n    smartTitle\n    summary\n  }\n\n\n\n  \n  fragment UserPost on Post {\n    read\n    upvoted\n    commented\n    bookmarked\n    downvoted\n  }\n\n\n',
                "variables": {
                    "version": 65,
                    "period": 7,
                    "first": 9,
                    "after": "",
                },
            }
            body = {
                "query": most_popular_query[
                    "query"
                ],  #'\n  query Feed(\n    $loggedIn: Boolean! = false\n    $first: Int\n    $after: String\n    $ranking: Ranking\n    $version: Int\n    $supportedTypes: [String!] = ["article","share","freeform","video:youtube","collection"]\n  ) {\n    page: feed(\n      first: $first\n      after: $after\n      ranking: $ranking\n      version: $version\n      supportedTypes: $supportedTypes\n    ) {\n      ...FeedPostConnection\n    }\n  }\n  \n  fragment FeedPostConnection on PostConnection {\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n    edges {\n      node {\n        ...FeedPost\n        contentHtml\n        ...UserPost @include(if: $loggedIn)\n      }\n    }\n  }\n  \n  fragment FeedPost on Post {\n    ...FeedPostInfo\n    sharedPost {\n      id\n      title\n      image\n      readTime\n      permalink\n      commentsPermalink\n      createdAt\n      type\n      tags\n      source {\n        id\n        handle\n        permalink\n        image\n      }\n      slug\n    }\n    trending\n    feedMeta\n    collectionSources {\n      handle\n      image\n    }\n    numCollectionSources\n    updatedAt\n    slug\n  }\n  \n  fragment FeedPostInfo on Post {\n    id\n    title\n    image\n    readTime\n    permalink\n    commentsPermalink\n    createdAt\n    commented\n    bookmarked\n    views\n    numUpvotes\n    numComments\n    summary\n    bookmark {\n      remindAt\n    }\n    author {\n      id\n      name\n      image\n      username\n      permalink\n    }\n    type\n    tags\n    source {\n      id\n      handle\n      name\n      permalink\n      image\n      type\n    }\n    userState {\n      vote\n      flags {\n        feedbackDismiss\n      }\n    }\n    slug\n  }\n\n  \n  fragment UserPost on Post {\n    read\n    upvoted\n    commented\n    bookmarked\n    downvoted\n  }\n\n\n',
                "variables": {
                    "version": 47,
                    "ranking": "POPULARITY",
                    "first": 10,
                    "loggedIn": True,
                    "after": after if after else None,
                    # "withDiscussedPosts": True,
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

        upvote_post_body = {
            "query": "\n  mutation Vote($id: ID!, $entity: UserVoteEntity!, $vote: Int!) {\n    vote(id: $id, entity: $entity, vote: $vote) {\n      _\n    }\n  }\n",
            "variables": {"id": articel_id, "vote": 1, "entity": "post"},
        }
        try:
            comment_response = requests.post(
                f"{self.api_url}", json=comment_body, headers=headers
            ).json()

            upvote_response = requests.post(
                f"{self.api_url}", json=upvote_post_body, headers=headers
            ).json()

            if (
                comment_response
                and "erros" in comment_response
                or (upvote_response and "erros" in upvote_response)
            ):
                print(
                    "error posting comments",
                    comment_response["erros"] or upvote_response["erros"],
                )
        except requests.RequestException as e:
            print(f"Error posting comment or like: {e}")
            return []

    # def construct_prompt(self, article_title: str, article_content: str) -> str:
    #     return (
    #         f"Please generate a human-like comment for a blog post within 2 lines. "
    #         f"The comment should be relevant, thoughtful. If you believe "
    #         f"there is nothing substantial to say about the content or it other then english language, return an empty string represented as <No/> \n"
    #         f"The blog title is {article_title}\n "
    #         f"<blog> {article_content}</blog>"
    #     )

    def construct_prompt(self, article_title: str, article_content: str) -> str:
        return (
            f"Please generate a short, human-like comment (within 2 lines) for the following blog post. "
            f"The comment should be relevant and thoughtful "
            f"If the content is trivial or not meaningful enough for a comment, or if it's not in English, return an empty string represented as <No/>. \n\n"
            f"Blog Title: {article_title}\n"
            f"Article Content:\n<blog>{article_content}</blog>"
        )

    def main(self):
        myfeed = {"data": {"page": {"pageInfo": {"hasNextPage": True, "endCursor": 0}}}}

        while myfeed["data"]["page"]["pageInfo"]["hasNextPage"]:
            myfeed = self.get_my_feed(myfeed["data"]["page"]["pageInfo"]["endCursor"])
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
    # commenter = DailyDev()
    # commenter.main()
    commenter = DevToCommenter()
    commenter.main()
