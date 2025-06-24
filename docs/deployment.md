### Overview

 Deploying to **Vercel** is supported, with dedicated buttons for the **Frontend** and **Backend** applications. Both require specific configurations during and after deployment to ensure proper functionality.

---

### Frontend Deployment

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fvintasoftware%2Fnextjs-fastapi-template%2Ftree%2Fmain%2Fnextjs-frontend&env=API_BASE_URL&envDescription=The%20API_BASE_URL%20is%20the%20backend%20URL%20where%20the%20frontend%20sends%20requests.)

- Click the **Frontend** button above to start the deployment process.  
- During deployment, you will be prompted to set the `API_BASE_URL`. Use a placeholder value (e.g., `https://`) for now, as this will be updated with the backend URL later.  
- Complete the deployment process [here](#post-deployment-configuration).

### Backend Deployment

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fvintasoftware%2Fnextjs-fastapi-template%2Ftree%2Fmain%2Ffastapi_backend&env=CORS_ORIGINS,ACCESS_SECRET_KEY,RESET_PASSWORD_SECRET_KEY,VERIFICATION_SECRET_KEY&stores=%5B%7B%22type%22%3A%22postgres%22%7D%5D)

- Click the **Backend** button above to begin deployment.
- First, set up the database. The connection is automatically configured, so follow the steps, and it should work by default.
- During the deployment process, you will be prompted to configure the following environment variables:

  - **CORS_ORIGINS**  
    - Set this to `["*"]` initially to allow all origins. Later, you can update this with the frontend URL.

  - **ACCESS_SECRET_KEY**, **RESET_PASSWORD_SECRET_KEY**, **VERIFICATION_SECRET_KEY**  
    - During deployment, you can temporarily set these secret keys as plain strings (e.g., `examplekey`). However, you should generate secure keys and update them after the deployment in the **Post-Deployment Configuration** section.

- Complete the deployment process [here](#post-deployment-configuration).


## CI (GitHub Actions) Setup for Production Deployment

We provide the **prod-backend-deploy.yml** and **prod-frontend-deploy.yml** files to enable continuous integration through Github Actions. To connect them to GitHub, simply move them to the .github/workflows/ directory.

You can do it with the following commands:
   ```bash
    mv prod-backend-deploy.yml .github/workflows/prod-backend-deploy.yml
    mv prod-frontend-deploy.yml .github/workflows/prod-frontend-deploy.yml
   ```

### Prerequisites
1. **Create a Vercel Token**:  
   - Generate your [Vercel Access Token](https://vercel.com/account/tokens).  
   - Save the token as `VERCEL_TOKEN` in your GitHub secrets.

2. **Install Vercel CLI**:  
   ```bash
   pnpm i -g vercel@latest
   ```
3. Authenticate your account.
    ```bash
   vercel login
   ```
### Database Creation (Required)

   1. **Choosing a Database**
      - You can use your database hosted on a different service or opt for the [Neon](https://neon.tech/docs/introduction) database, which integrates seamlessly with Vercel.

   2. **Setting Up a Neon Database via Vercel**
      - In the **Projects dashboard** page on Vercel, navigate to the **Storage** section.  
      - Select the option to **Create a Database** to provision a Neon database.

   3. **Configuring the Database URL**
      - After creating the database, retrieve the **Database URL** provided by Neon.  
      - Include this URL in your **Environment Variables** under `DATABASE_URL`.  

   4. **Migrating the Database**
      - The database migration will happen automatically during the GitHub action deployment, setting up the necessary tables and schema.
### Frontend Setup

1. Link the nextjs-frontend Project

2. Navigate to the nextjs-frontend directory and run:
   ```bash
   cd nextjs-frontend
   vercel link
   ```
3. Follow the prompts:
   - Link to existing project? No
   - Modify settings? No

4. Save Project IDs and Add GitHub Secrets:
  - Open `nextjs-frontend/.vercel/project.json` and add the following to your GitHub repository secrets:
    - `projectId` → `VERCEL_PROJECT_ID_FRONTEND`
    - `orgId` → `VERCEL_ORG_ID`

### Backend Setup

1. Link the fastapi_backend Project

2. Navigate to the fastapi_backend directory and run:
   ```bash
   cd fastapi_backend
   vercel link --local-config=vercel.prod.json
   ```
   - We use a specific configuration file to set the --local-config value.
3. Follow the prompts:
   - Link to existing project? No
   - Modify settings? No

4. Save Project IDs and Add GitHub Secrets:
  - Open `fastapi_backend/.vercel/project.json` and add the following to your GitHub repository secrets:
    - `projectId` → `VERCEL_PROJECT_ID_BACKEND`
    - `orgId` → `VERCEL_ORG_ID` (Only in case you haven't added that before)

5. Update requirements.txt file:
      ```bash
      cd fastapi_backend
      uv export > requirements.txt
      ```
  - Export a new requirements.txt file is required to vercel deploy when the uv.lock is modified.

### Notes
- Once everything is set up, run `git push`, and the deployment will automatically occur.
- Please ensure you complete the setup for both the frontend and backend separately.
- Refer to the [Vercel CLI Documentation](https://vercel.com/docs/cli) for more details.
- You can find the project_id into the vercel web project settings.
- You can find the organization_id into the vercel web organization settings.

## Post-Deployment Configuration

### Frontend
   - Navigate to the **Settings** page of the deployed frontend project.  
   - Access the **Environment Variables** section.  
   - Update the `API_BASE_URL` variable with the backend URL once the backend deployment is complete.

### Backend
   - Access the **Settings** page of the deployed backend project.  
   - Navigate to the **Environment Variables** section and update the following variables with secure values:

     - **CORS_ORIGINS**  
       - Once the frontend is deployed, replace `["*"]` with the actual frontend URL.

     - **ACCESS_SECRET_KEY**  
       - Generate a secure key for API access and set it here.  

     - **RESET_PASSWORD_SECRET_KEY**
       - Generate a secure key for password reset functionality and set it.

     - **VERIFICATION_SECRET_KEY**  
       - Generate a secure key for user verification and configure it.

   - For detailed instructions on setting these secret keys, please look at the section on [Setting up Environment Variables](get-started.md#setting-up-environment-variables).

### Fluid serverless activation
[Fluid](https://vercel.com/docs/functions/fluid-compute) is Vercel's new concurrency model for serverless functions, allowing them to handle multiple 
requests per execution instead of spinning up a new instance for each request. This improves performance, 
reduces cold starts, and optimizes resource usage, making serverless workloads more efficient.

Follow this [guide](https://vercel.com/docs/functions/fluid-compute#how-to-enable-fluid-compute) to activate Fluid.
