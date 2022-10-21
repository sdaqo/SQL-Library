CREATE TABLE "user_types" (
	"id"	INTEGER,
	"title"	TEXT,
	"deadline" INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "media_types" (
	"id"	INTEGER,
	"title"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "authors" (
	"id" INTEGER,
	"name" TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)

CREATE TABLE "users" (
	"id"	INTEGER,
	"name"	TEXT,
	"surename"	TEXT,
	"email"	TEXT UNIQUE,
	"pwdhash" TEXT,
	"birthday"	TEXT,
	"user_type"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("user_type") REFERENCES "user_types"("id")
);

CREATE TABLE "media" (
	"id"	INTEGER,
	"title"	TEXT,
	"media_type_id"	INTEGER,
	"isbn"	INTEGER UNIQUE,
	"age_limit"	INTEGER,
	"author_id" INTEGER,
	FOREIGN KEY("media_type_id") REFERENCES "media_types"("id"),
	FOREIGN KEY("author_id") REFERENCES "authors"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "borrowings" (
	"id"	INTEGER,
	"media_id"	INTEGER,
	"user_id"	INTEGER,
	"borrow_date"	INTEGER,
	"return_date"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("media_id") REFERENCES "media"("id"),
	FOREIGN KEY("user_id") REFERENCES "users"("id")
);
