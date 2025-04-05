# Topic 10. Additional Topics in Backend Development

In this homework assignment, you will continue improving your REST API application from the previous assignment.

---

## Technical Description of the Task

1. **Implement an authentication mechanism in the application.**

2. **Implement an authorization mechanism using JWT tokens** so that all operations on contacts are conducted only by registered users.

3. **Users should only have access to their own contact operations.**

4. **Implement email verification for registered users.**

5. **Limit the number of requests to the `/me` route.**

6. **Enable CORS for your REST API.**

7. **Add the ability for users to update their avatars** (use the Cloudinary service).

---

## General Requirements for Completing the Assignment

The requirements below are mandatory for the mentor's evaluation. If any of these requirements are not met, the assignment will be returned by the mentor for revisions without grading.  
If you’re “just clarifying” 😉 or “stuck” at any stage, feel free to reach out to your mentor in Slack.

- During registration, if a user with the same email already exists, the server must return an HTTP 409 Conflict error.
- The server must hash passwords and not store them in plain text in the database.
- Upon successful registration, the server must return an HTTP 201 Created response status and the new user data.
- For all POST operations (creating a new resource), the server must return a status of HTTP 201 Created.
- During POST operations, user authentication is required. The server must accept a request with user data (name and password) in the request body.
- If the user does not exist or the password is incorrect, the server must return an HTTP 401 Unauthorized error.
- The authorization mechanism using JWT tokens must utilize an `access_token` for access.
- All environment variables must be stored in a `.env` file. There should be no sensitive data hardcoded in the application.
- **Docker Compose** must be used to run all services and databases in the application.
