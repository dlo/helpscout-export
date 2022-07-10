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
    INTEGER id
    TEXT first_name
    TEXT last_name
    TEXT gender
    TEXT photo_type
    TEXT photo_url
    DATETIME created_at
    DATETIME updated_at
  }

  mailbox {
    INTEGER id
    TEXT name
    TEXT slug
    TEXT email
    DATETIME created_at
    DATETIME updated_at
  }

  tag {
    INTEGER id
    TEXT slug
    TEXT name
    TEXT color
    DATETIME created_at
    INT ticket_count
  }

  "user" {
    INTEGER id
    TEXT first_name
    TEXT last_name
    TEXT email
    TEXT role
    TEXT timezone
    DATETIME created_at
    DATETIME updated_at
    TEXT type_
    TEXT mention
    TEXT initials
    TEXT job_title
    TEXT phone
    TEXT alternate_emails
  }

  address {
    TEXT city
    TEXT lines
    TEXT state
    TEXT postal_code
    TEXT country
    INTEGER customer_id
  }

  chat {
    INTEGER id
    TEXT value
    INTEGER customer_id
  }

  conversation {
    INTEGER id
    INTEGER _number
    INTEGER threads
    TEXT _type
    INTEGER folder_id
    TEXT status
    TEXT state
    TEXT subject
    TEXT preview
    INTEGER mailbox_id
    INTEGER assignee_id
    INTEGER created_by_id
    DATETIME created_at
    INTEGER closed_by
    INTEGER closed_by_user_id
    DATETIME user_updated_at
    DATETIME customer_waiting_since
    TEXT source
    TEXT tags
    TEXT cc
    TEXT bcc
    INTEGER primary_customer_id
  }

  email {
    INTEGER id
    TEXT value
    INTEGER customer_id
  }

  phone {
    INTEGER id
    TEXT value
    TEXT _type
    INTEGER customer_id
  }

  social_profile {
    INTEGER id
    TEXT value
    TEXT _type
    INTEGER customer_id
  }

  thread {
    INTEGER id
    TEXT _type
    TEXT status
    TEXT state
    TEXT action
    TEXT body
    TEXT source
    INTEGER customer_id
    INTEGER created_by_id
    INTEGER assigned_to_id
    INTEGER saved_reply_id
    TEXT _to
    TEXT cc
    TEXT bcc
    DATETIME created_at
  }

  website {
    INTEGER id
    TEXT value
    INTEGER customer_id
  }

  workflow {
    INTEGER id
    INTEGER mailbox_id
    TEXT _type
    TEXT status
    INT _order
    TEXT name
    DATETIME created_at
    DATETIME modified_at
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
  "user" ||--o{ conversation : "foreign key"
  "user" ||--o{ thread : "foreign key"
```
