import zlib
import base64
import json

# The encoded string provided by the user
encoded_str = "eJyEk0FzozgQhX8N3OwSkhDmwCFrLxWcgNcb4sS-UEIIEEZAhDCBX7-FszM1OUzNUWr1p6fXT4xqXrRq8nLF-aoXRTN0K9Y2uVCSatE2ZuYhNwUbRkzuWQ7EBKGNA0wuqaiTgjdcUc2zhOqfVeK6gJilxzcM5baVEghyDF0nZciCVoYA5hQAaJnCgwBisIEEANvBzhqtsU0ckKYky52c4dxaN9mt3OSjMjCQxSqz1v2Q9pqy65q10hR9sghftHhaDdysvVLrrjfQgwF9A_qdagtFpeRK0Yp-azagTzthQP9mGdBfMAb0_3-6gXzdXnljoB2f9haDp-kd1tegaqdwF45RXHwe4mMfNFHNUNSl0N5ftgEJZLmNa7cK_b3N62734rt_HVFhv8zX8fUx8w--fzrEp_EsSxSIUdD3B3EQAQy3eIp24RDN1yGaX8Xzdt-d34_iUP2NwuoIwznEUcX6QJ4w2wYkjNkUzcEUxQWMpoUTzUHVCvZ4Es9xAMPdGYTVeeHM2VsgDmIvmTzVz2_RLZWXjkkg8uPa_tjOwcfq6TI2ZXl86j8vp7QL_4kcEsg35ubDh8b_XsptjEYDkoZ_agPtvvyF9uKwvXhs_8FlG_rLBlMi5UufP2iZ9O2g2H25-zVtyX2USw-phl4nSyB5lgzd_eR9wt2QJqyVcmiEnhLe0LTmmfejVAv2BRKZBwkgGBJTeV1NGe-1ag0MiuWGe3j6Ic1aSUXjfddv6t__hqHn6s4GCNgby8XmzYP_BQAA__8Y3Bpn"

# Fixing the URL-safe base64 encoding by replacing '-' and '_' with '+' and '/'
encoded_str_fixed = encoded_str.replace("-", "+").replace("_", "/")

# Decoding the base64 encoded string
decoded_bytes = base64.b64decode(encoded_str_fixed)

# Attempting to decompress the data using zlib
try:
    decompressed_data = zlib.decompress(decoded_bytes)
    result = decompressed_data.decode("utf-8")
except Exception as e:
    result = str(e)

print(result)  # Display the first 500 characters for context (if it's long)
# [
#     "category",
#     "d",
#     "e",
#     "email_generated_at",
#     "h",
#     "i",
#     "is_freemail",
#     "l",
#     "pub_community_enabled",
#     "publication_id",
#     "r",
#     "subdomain",
#     "t",
#     "user_id",
#     "v"
# ]
# [
#     "free-signup-confirmation",
#     "39b08c6",
#     "1724633870",
#     "1724633869906",
#     "e8c3f51b620f4297bc3121d304ea0021",
#     "20240826005747.3.45670bb6df7fc4f1.ndvh8fwr@mg-d1.substack.com",
#     "true",
#     "https://programmerraja.substack.com/api/v1/free/confirm?token=eyJ1c2VyX2lkIjoyMDMwNTgxOTQsInNlc3Npb25JZCI6ImhCTl9jMFJ5elpDSF9BQ3g5SzkwUHdFOFFVOTVwYmh3IiwiaXAiOiI2MC4yNDMuNzkuNzUiLCJpYXQiOjE3MjQ2MzM4NjcsImV4cCI6MTcyNzIyNTg2NywiaXNzIjoicHViLTI2MDY0MjYiLCJzdWIiOiJmcmVlLWNvbmZpcm0ifQ.5qCzIq-KZwnhhQKsxZVbpMPN76ImWc9fuqt4RZhCT3w&next=https%3A%2F%2Fprogrammerraja.substack.com%2Fsubscribe%3Futm_source%3Dconfirmation_email%26just_signed_up%3Dtrue",
#     "true",
#     "2606426",
#     "placestro@gmail.com",
#     "programmerraja",
#     "free-signup-confirmation",
#     "203058194",
#     "2"
# ]


# The JWT string provided by the user
jwt_token = "eyJ1c2VyX2lkIjoyMDMwNTgxOTQsInNlc3Npb25JZCI6ImhCTl9jMFJ5elpDSF9BQ3g5SzkwUHdFOFFVOTVwYmh3IiwiaXAiOiI2MC4yNDMuNzkuNzUiLCJpYXQiOjE3MjQ2MzM4NjcsImV4cCI6MTcyNzIyNTg2NywiaXNzIjoicHViLTI2MDY0MjYiLCJzdWIiOiJmcmVlLWNvbmZpcm0ifQ.5qCzIq-KZwnhhQKsxZVbpMPN76ImWc9fuqt4RZhCT3w"

# Let's first check how many parts the token has
parts = jwt_token.split(".")

# Decoding the first part which likely contains the header and payload
decoded_first_part = base64.urlsafe_b64decode(parts[0] + "==").decode("utf-8")

# Trying to parse it as JSON
decoded_json = json.loads(decoded_first_part)
print(decoded_json)
