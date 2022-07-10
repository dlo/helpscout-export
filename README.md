# helpscout-export

I wanted to export all my Help Scout data to a SQLite database. I searched and couldn't find anything that did this well, so I wrote it myself.

To run this script, create a new App via "Profile" > "My Apps" > "Create My App". Give it a name and a redirection URL (can be anything). Once the app is created, export `HELPSCOUT_APP_ID` and `HELPSCOUT_APP_SECRET` in your shell, then run the following to download all your data.

```
make install-dependencies
make download
```

All of your Help Scout data will be downloaded to a directory named `data/`. To import this data into a SQLite database, run this next:

```
make import
```

This will import all of the downloaded data to a SQLite file in the directory (`helpscout.db`).

Here's the ER diagram:

```mermaid
erDiagram

  customer {
  }

  mailbox {
  }

  tag {
  }

  user {
  }

  email {
  }

  phone {
  }

  social_profile {
  }

  thread {
  }

  website {
  }

  workflow {
  }

  customer ||--o{ address : "foreign key"
  customer ||--o{ chat : "foreign key"
  customer ||--o{ conversation : "foreign key"
  customer ||--o{ email : "foreign key"
  customer ||--o{ phone : "foreign key"
  customer ||--o{ social_profile : "foreign key"
  customer ||--o{ thread : "foreign key"
  customer ||--o{ website : "foreign key"
  mailbox ||--o{ workflow : "foreign key"
  user ||--o{ conversation : "foreign key"
  user ||--o{ thread : "foreign key"
```
