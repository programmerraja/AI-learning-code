#!/usr/bin/env node

const axios = require("axios");
const readline = require("readline");

const sourceIds = {
  // AI: "a6581605-a03b-4877-84f2-7d362a8ada28",
  "AI ❤️ JS": "33f80cec-bf85-40a3-b3e1-c34718b1b7d7",
  // "AI Newsroom": "5d72adc4-96ff-490a-9c3c-57f4625ce342",
  // "Best stories": "c99d10fc-a827-40ee-964a-7deabf414873",
  "Build With GenAI": "810b1941-d94d-4167-8461-556c50d1e430",
  // "Byte-Sized Insights": "f256bc9a-e674-4693-88ef-a269646562db",
  // "Chief Suffering Officer": "38e44303-9897-4013-bacc-f624ab8a40f3",
  // Cloud: "6c4054c4-9a66-429d-9036-c0bc83592f8a",
  // "controversy.dev": "12b10915-9467-4fcf-a72b-75504c4cf304",
  // "daily.dev World": "a1f0092b-0ee1-414b-82e6-f2c92d7335e4",
  "Deep Learning": "5bd24a22-5b0e-4038-816a-e406bc789de9",
  // "Developer Relations": "73b32282-f25a-4634-b44f-cd184fb3b9a6",
  "Developers Squad": "e91381f7-a18c-4bc8-9f9f-ef73b6e4f141",
  // DevOps: "6712c17d-f3dd-4c9f-9eaa-cef0fdeb5808",
  "Dev Squad": "8a09782e-202a-450f-afda-d4dd3ae97589",
  "Dev Tools": "d81dba65-6ea7-4c6b-a547-2f9ba493ddd2",
  "Dev World": "81a3df5b-e17a-41f0-ae4f-8035927c6518",
  // DiamantAI: "1d002e3a-2177-48e1-b9f4-33f8a09565dd",
  // "Engineering Leadership": "1c73f1ee-c7fb-492d-8ac2-0d1ba72dc72a",
  "Fullstack Developer": "263b405b-96f2-46b1-ba7e-41068c375d2e",
  // "Go Developers": "6fc8295e-5271-40f3-9a48-2a5b42f7c85a",
  // "Indie Startups": "bd530c80-cb3a-4494-879e-9749bc864788",
  "JS Development": "f9ae09a2-50d0-4c46-af92-fa6627654fd3",
  // KubeSquad: "ee9190a8-e125-44a1-ae91-29136b970c81",
  // LeleOnTech: "9ad8c42e-2e33-4dbd-8d40-f580df3ceb34",
  // "Machine Learning": "d7de1c7d-8971-401a-880d-481b01adc4c6",
  "Machine Learning News": "marktechpost",
  "ML & AI": "1ec69b57-19c4-4852-b196-6d9948e10bdb",
  // "Node.js developers": "8ccb5b29-1050-49ed-9fd4-d553890497b5",
  // OpenSouls: "9d623694-d571-4722-9b36-9f1961edb811",
  // RAG: "d0e33bd4-4386-42bd-a7d8-338c0ade11c7",
  Syntax: "3d6083c9-3b6b-4bef-a4ea-392835291ee0",
  "Tamil:DevCommunity": "bdf405c4-faee-4e97-b2e2-f63cfc86b45d",
  // "The Dev Craft": "db9d9c61-7296-4ef0-9d4d-62dc93b197fa",
  "Vibe Coding": "ad08ba59-6646-487f-a8bd-2147d9e572a6",
  "Web & App Development": "7c5977dc-7115-4498-a755-15a6dcf562c4",
  WebCraft: "ad378b4e-6140-40ea-b7d8-4c54fc2525a5",
  WeProDev: "c15cda32-e271-4808-b5fe-6a55b4a8b6b4",
};

const COOKIE_DA2 =
  "da2=NbQgWXH9JdceQ4lfD3WCY; das=e5fa3ec3-3355-49ad-8842-54c05ece3fbe; _tt_enable_cookie=1; _ttp=01K0DK9WC6B44M6YXWAQ1EZR2X_.tt.1; ilikecookies=true; _cfuvid=LKSepkH1y0TUw5QVY4CFBQOvmCmEuO5DdH90rAAhrcY-1762729600578-0.0.1.1-604800000; _vwo_uuid_v2=D768EB5B03301358DEE02A4F847AC391A|589ffc6b0072592f7b8a9a60c6529b24; _ga_88PBR8PHX0=GS2.1.s1762729601$o1$g0$t1762729601$j60$l0$h0; _ga=GA1.1.840969628.1722752906; _ga_Y94RMTGW0M=GS2.1.s1764580362$o8$g1$t1764580378$j44$l0$h0; _rdt_uuid=1752803109031.7c49e1c8-c080-41ea-80c9-c5cb600f2db9; ttcsid=1768905218297::QM7Lc8PU5Sv_oakW7jUj.11.1768905400915.0; ttcsid_CO2RCPBC77U37LT1TAIG=1768905218297::dQtBs4iqeGuU_u72Na-b.11.1768905400915.1; _ga_VTGLXD7QSN=GS2.1.s1768903865$o15$g1$t1768905403$j58$l0$h0; ory_kratos_session=MTc3MTgyMjQzMHxjdGpXOFZDekhLWk4yUTZ3NnBQYVdFYWVUVTk2eVl1Q1FDNWI5UXlOVXdJNWRUMzFhMlNFYWg1dEx6WlFZNUxkWm1FUEpLTnBJNWZYUWVnaXdseldtOS0wbG5BY09LZncwX21vXzhrLWdXRUFzTzRTRVQtdVlqdTJVSDJhdklWSWNLT29IbXJyRGpsZWdROWt6M0l5WlkwLW51YmdGYnZ5R01odVlZZVRsaTlwUXlDU3lkeDZFZW9nR1kxOXFVNWIzNEhISVN4bTJ4clRtTE1kV1pqb1hfa2dTS2JwTHhkS1llTEozTXFaQ0dmUGJPZURPdWFSRVdKNXVHRjVNZ3NxTVQzUDRnY2JrQ0JEd1JIQXxLx5CDWLpNH1bq9vL76Ay70ETmthTnhzGaOqh-5yi3Rg==; da3=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzIzODA5NjAuNzc0LCJ1c2VySWQiOiJOYlFnV1hIOUpkY2VRNGxmRDNXQ1kiLCJyb2xlcyI6W10sImlzVGVhbU1lbWJlciI6ZmFsc2UsImlzUGx1cyI6ZmFsc2UsImlhdCI6MTc3MjM4MDA2MCwiYXVkIjoiRGFpbHkiLCJpc3MiOiJEYWlseSBBUEkifQ.Xwda4o-M_n5-JyvZ5J_UUt5Kbxjp8qkfyITLHrVRzsmW3gwxEX3OXrPkfrYmhOxUKibp-yL-k-lW9rp-ebw2a68N0tnT_S-zpKzW8IXJkeQW9VIEgKKXyuOZEsTBtOFXTD1UlW6QaBJ0gDc4djueeaA_DzWt_XoG4Y_eTf_nOVmHr7WAs2Zi4cXn4GqilLGzbek5xmGgiRCtc8Apa88G20n4BsGaACAt9gHCD6c7JXHg15gVEeNOz6PI_CpQNcSuwbFzEVal6FaFlfaxQ2shthLU3b_DVqyZz0mie9EgJZmYOOOSpopN0J8K39fUZvXCiPGveXBOd9QunLHb7hZYWQ.vNtE4ETsoiZNyWM6c8RZgNp9yRN21wPA0q6eOJx%2FykY";
const title = "Sherlock Holmes: The Case Of AI Brought Down Our Servers";
const sharedPostIdOrLink =
  "https://medium.com/@programmerraja/sherlock-holmes-the-case-of-ai-brought-down-our-servers-e3d748912f96"; // or a post ID

async function getPreviewid(url) {
  try {
    return "https://miro.medium.com/v2/resize:fit:1200/1*B3LLLwvGSV6DTuGQVeEILw.png";
    const query = `mutation CheckLinkPreview($url: String!) {
    checkLinkPreview(url: $url) {
      id
      title
      image
      url
      relatedPublicPosts {
        id
        title
        permalink
        createdAt
        source {
          id
          name
          image
          type
        }
        author {
          id
          image
          username
        }
      }
    }
  }

    `;

    const variables = {
      url: url,
    };

    const headers = {
      "accept-language": "en-US,en;q=0.9",
      "cache-control": "no-cache",
      "content-type": "application/json",
      cookie: `${COOKIE_DA2}`,
      dnt: "1",
      origin: "https://app.daily.dev",
      pragma: "no-cache",
      referer: "https://app.daily.dev/",
      "sec-ch-ua":
        '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": '"Linux"',
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "cors",
      "sec-fetch-site": "same-site",
      "user-agent":
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    };

    const response = await axios.post(
      "https://api.daily.dev/graphql",
      { query, variables },
      { headers },
    );

    const data = response.data;

    if (data.errors) {
      console.error("❌ API Error:", data.errors);
      return null;
    }

    // Return the shared post ID
    console.log("✅ Link preview ID:", data.data.checkLinkPreview.id);
    return data.data.checkLinkPreview.id;
  } catch (err) {
    console.error("❌ Request failed:", err);
    return null;
  }
}
async function main() {
  if (!title || !sharedPostIdOrLink) {
    console.error(
      "Usage: node shareToDailyDev.js <title> <sharedPostIdOrLink>",
    );
    process.exit(1);
  }

  const previewid = await getPreviewid(sharedPostIdOrLink);

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  for (const name of Object.keys(sourceIds)) {
    const sourceName = name;

    // Ask user to confirm
    const answer = "sss";
    // await new Promise((resolve) => {
    //   rl.question(
    //     `\nPost to "${sourceName}"? (Press Enter to continue, type 's' to skip): `,
    //     resolve
    //   );
    // });

    if (answer.toLowerCase() === "s") {
      console.log(`⏭ Skipping "${sourceName}"`);
      continue;
    }

    const query = `
      mutation CreateSourcePostModeration(
        $sourceId: ID!,
        $type: String!,
        $title: String,
        $sharedPostId: ID,
        $externalLink: String
      ) {
        createSourcePostModeration(
          sourceId: $sourceId,
          type: $type,
          title: $title,
          sharedPostId: $sharedPostId,
          externalLink: $externalLink
        ) {
          id
          title
        }
      }
    `;

    const isLink = sharedPostIdOrLink.startsWith("http");
    const variables = {
      type: "share",
      sourceId: sourceIds[sourceName],
      imageUrl: previewid,
      title,
      commentary: title,
      ...(isLink
        ? { externalLink: sharedPostIdOrLink }
        : { sharedPostId: sharedPostIdOrLink }),
    };

    const headers = {
      "Content-Type": "application/json",
      "User-Agent": "Mozilla/5.0",
      Referer: "https://app.daily.dev/",
      Cookie: `${COOKIE_DA2}`,
    };

    try {
      const response = await axios.post(
        "https://api.daily.dev/graphql",
        { query, variables },
        { headers },
      );

      const json = response.data;

      if (json.errors) {
        console.error("❌ API Error:", json.errors);
      } else {
        console.log("✅ Post created:", JSON.stringify(json.data, null, 2));
      }

      // Small delay to avoid hitting rate limits
      await new Promise((r) => setTimeout(r, 30000)); // 30 sec
    } catch (err) {
      console.error("❌ Request failed:", err);
    }
  }

  rl.close();
}

main().catch(console.error);
