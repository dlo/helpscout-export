DROP TABLE IF EXISTS thread;
CREATE TABLE thread(
  id INTEGER PRIMARY KEY,
  _type TEXT,
  status TEXT,
  state TEXT,
  action TEXT,
  body TEXT,
  source TEXT,
  customer_id INTEGER,
  created_by_id INTEGER,
  assigned_to_id INTEGER,
  saved_reply_id INTEGER,
  _to TEXT,
  cc TEXT,
  bcc TEXT,
  created_at DATETIME,
  FOREIGN KEY (created_by_id) REFERENCES user(id),
  FOREIGN KEY (assigned_to_id) REFERENCES user(id),
  FOREIGN KEY (customer_id) REFERENCES customer(id)
);

DROP TABLE IF EXISTS conversation;
CREATE TABLE conversation(
  id INTEGER PRIMARY KEY,
  _number INTEGER,
  threads INTEGER,
  _type TEXT,
  folder_id INTEGER,
  status TEXT,
  state TEXT,
  subject TEXT,
  preview TEXT,
  mailbox_id INTEGER,
  assignee_id INTEGER,
  created_by_id INTEGER,
  created_at DATETIME,
  closed_by INTEGER,
  closed_by_user_id INTEGER,
  user_updated_at DATETIME,
  customer_waiting_since DATETIME,
  source TEXT,
  tags TEXT,
  cc TEXT,
  bcc TEXT,
  primary_customer_id INTEGER,
  FOREIGN KEY (assignee_id) REFERENCES user(id),
  FOREIGN KEY (closed_by_user_id) REFERENCES user(id),
  FOREIGN KEY (primary_customer_id) REFERENCES customer(id),
  FOREIGN KEY (created_by_id) REFERENCES customer(id)
);

DROP TABLE IF EXISTS chat;
CREATE TABLE chat(
  id INTEGER PRIMARY KEY,
  value TEXT,
  _type TEXT
);

DROP TABLE IF EXISTS mailbox;
CREATE TABLE mailbox(
  id INTEGER PRIMARY KEY,
  name TEXT,
  slug TEXT,
  email TEXT,
  created_at DATETIME,
  updated_at DATETIME
);

DROP TABLE IF EXISTS workflow;
CREATE TABLE workflow(
  id INTEGER PRIMARY KEY,
  mailbox_id INTEGER,
  _type TEXT,
  status TEXT,
  _order INT,
  name TEXT,
  created_at DATETIME,
  modified_at DATETIME,
  FOREIGN KEY (mailbox_id) REFERENCES mailbox(id)
);

DROP TABLE IF EXISTS tag;
CREATE TABLE tag(
  id INTEGER PRIMARY KEY,
  slug TEXT,
  name TEXT,
  color TEXT,
  created_at DATETIME,
  ticket_count INT
);

DROP TABLE IF EXISTS user;
CREATE TABLE user(
  id INTEGER PRIMARY KEY,
  first_name TEXT,
  last_name TEXT,
  email TEXT,
  role TEXT,
  timezone TEXT,
  created_at DATETIME,
  updated_at DATETIME,
  type_ TEXT,
  mention TEXT,
  initials TEXT,
  job_title TEXT,
  phone TEXT,
  alternate_emails TEXT
);

DROP TABLE IF EXISTS customer;
CREATE TABLE customer(
  id INTEGER PRIMARY KEY,
  first_name TEXT,
  last_name TEXT,
  gender TEXT,
  photo_type TEXT,
  photo_url TEXT,
  created_at DATETIME,
  updated_at DATETIME
);

DROP TABLE IF EXISTS address;
CREATE TABLE address(
  city TEXT,
  lines TEXT,
  state TEXT,
  postal_code TEXT,
  country TEXT,
  customer_id INTEGER,
  FOREIGN KEY (customer_id) REFERENCES customer(id)
);

DROP TABLE IF EXISTS chat;
CREATE TABLE chat(
  id INTEGER PRIMARY KEY,
  value TEXT,
  customer_id INTEGER,
  FOREIGN KEY (customer_id) REFERENCES customer(id)
);

DROP TABLE IF EXISTS email;
CREATE TABLE email(
  id INTEGER PRIMARY KEY,
  value TEXT,
  customer_id INTEGER,
  FOREIGN KEY (customer_id) REFERENCES customer(id)
);

DROP TABLE IF EXISTS phone;
CREATE TABLE phone(
  id INTEGER PRIMARY KEY,
  value TEXT,
  _type TEXT,
  customer_id INTEGER,
  FOREIGN KEY (customer_id) REFERENCES customer(id)
);

DROP TABLE IF EXISTS website;
CREATE TABLE website(
  id INTEGER PRIMARY KEY,
  value TEXT,
  customer_id INTEGER,
  FOREIGN KEY (customer_id) REFERENCES customer(id)
);

DROP TABLE IF EXISTS social_profile;
CREATE TABLE social_profile(
  id INTEGER PRIMARY KEY,
  value TEXT,
  _type TEXT,
  customer_id INTEGER,
  FOREIGN KEY (customer_id) REFERENCES customer(id)
);

