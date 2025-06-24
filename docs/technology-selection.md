This template streamlines building APIs with [FastAPI](https://fastapi.tiangolo.com/) and dynamic frontends with [Next.js](https://nextjs.org/). It integrates the backend and frontend using [@hey-api/openapi-ts](https://github.com/hey-ai/openapi-ts) to generate a type-safe client, with automated watchers to keep the OpenAPI schema and client updated, ensuring a smooth and synchronized development workflow.  

- [Next.js](https://nextjs.org/): Fast, SEO-friendly frontend framework  
- [FastAPI](https://fastapi.tiangolo.com/): High-performance Python backend  
- [SQLAlchemy](https://www.sqlalchemy.org/): Powerful Python SQL toolkit and ORM
- [PostgreSQL](https://www.postgresql.org/): Advanced open-source relational database
- [Pydantic](https://docs.pydantic.dev/): Data validation and settings management using Python type annotations
- [Zod](https://zod.dev/) + [TypeScript](https://www.typescriptlang.org/): End-to-end type safety and schema validation  
- [fastapi-users](https://fastapi-users.github.io/fastapi-users/): Complete authentication system with:
    - Secure password hashing by default
    - JWT (JSON Web Token) authentication
    - Email-based password recovery
- [Shadcn/ui](https://ui.shadcn.com/): Beautiful and customizable React components
- [OpenAPI-fetch](https://github.com/Hey-AI/openapi-fetch): Fully typed client generation from OpenAPI schema  
- [fastapi-mail](https://sabuhish.github.io/fastapi-mail/): Efficient email handling for FastAPI applications
- [uv](https://docs.astral.sh/uv/): An extremely fast Python package and project manager
- [Pytest](https://docs.pytest.org/): Powerful Python testing framework
- Code Quality Tools:
    - [Ruff](https://github.com/astral-sh/ruff): Fast Python linter
    - [ESLint](https://eslint.org/): JavaScript/TypeScript code quality
- Hot reload watchers:  
    - Backend: [Watchdog](https://github.com/gorakhargosh/watchdog) for monitoring file changes  
    - Frontend: [Chokidar](https://github.com/paulmillr/chokidar) for live updates  
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/): Consistent environments for development and production
- [MailHog](https://github.com/mailhog/MailHog): Email server for development
- [Pre-commit hooks](https://pre-commit.com/): Enforce code quality with automated checks  
- [OpenAPI JSON schema](https://swagger.io/specification/): Centralized API documentation and client generation  

With this setup, you'll save time and maintain a seamless connection between your backend and frontend, boosting productivity and reliability.
