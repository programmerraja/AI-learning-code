- Is the code clean, readable, and maintainable?
- Are functions and variables clearly and consistently named?
- Is there any unnecessary or duplicate code that can be optimized?
- Check for code duplication deos the code can be reused
- Does the code follow [Node.js]/[JavaScript] best practices (e.g., naming conventions, avoiding global variables)?
- Are there any anti-patterns (e.g., nested callbacks, blocking code in async functions)?
- Are ES6+ features properly used (e.g., async/await, destructuring, template literals)?
- Are errors properly handled, or are they just being thrown unnecessarily? If so, request removal.
- See if adequate comments are added for any hacks/workarounds
- Are there any potential performance bottlenecks?
- Is the code optimized for scalability (e.g., proper use of async operations, avoiding blocking code)?
- can Multiple promise can combine in to single promise.all if they are independent promise
- Are there any security risks (e.g., unvalidated user input, improper error messages, unsanitized data)?
- Do queries include projection, and are they properly indexed?
- Is there an N+1 query problem?
- Is the schema well-structured, avoiding default negative values
- Is atomicity handled by the database (e.g., reducing credits  in the DB instead of in memory)?
- If `JSON.parse(JSON.stringify())` is used to get plain objects from Mongoose, suggest using `lean()` instead.