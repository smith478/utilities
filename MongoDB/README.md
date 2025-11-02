## Step 1: Run the MongoDB Docker Container

This command will start a MongoDB container, create a root user, and set up a volume to persist your data.

```bash
docker run -d \
  --name scryglass-mongo \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=your_root_password \
  -v scryglass-mongo-data:/data/db \
  mongo
```

Note: Replace `your_root_password` with a secure password. The `-v scryglass-mongo-data:/data/db` part creates a Docker volume named
`scryglass-mongo-data` to ensure your database data persists even if you remove the container.

## Step 2: Create a Dedicated Application User (Best Practice)

It's a best practice not to use the root user for your application. The following steps will guide you through creating a specific
user for the scryglass application.

1. Connect to the MongoDB instance inside the container:

```bash
docker exec -it scryglass-mongo mongosh -u admin -p your_root_password --authenticationDatabase admin
```

2. Inside the `mongosh` shell, create the database and the application user:

Copy and paste the following JavaScript code into the mongosh prompt. This will create a user named `scryglass_user` with the
necessary permissions for the `scryglass_db` database.

```javascript
use scryglass_db;

db.createUser({
  user: "scryglass_user",
  pwd: "your_app_password",
  roles: [
    { role: "readWrite", db: "scryglass_db" },
    { role: "dbAdmin", db: "scryglass_db" }
  ]
 });
```

Note: Replace `your_app_password` with a secure password for your application user. The dbAdmin role is necessary because the
application code needs to create collections and indexes.

You can then type exit to leave the mongosh shell.

## Step 3: Configure Your .env File

Now, you can use the credentials for the dedicated application user you just created in your .env file:

```yaml
MONGO_USER=scryglass_user
MONGO_PASSWORD=your_app_password
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=scryglass_db
```

With these steps, you'll have a local MongoDB instance running in Docker, following best practices by using a dedicated,
non-root user for your application.