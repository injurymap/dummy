# Project Initialization

The project should be run in VS Code Dev Container. (Ctrl + Shift + P > Reopen Folder in Dev Container)

1. Create local database with:

```
su - postgres
createdb postgres
```

2. Initialize DB scheme:

```
flask db upgrade
```

3. Run application from VS Code "Run and Debug" tab - "Python: Flask"
