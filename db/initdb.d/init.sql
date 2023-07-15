-- docker-compose.yamlのみで使用
use bookshelf;

CREATE TABLE IF NOT EXISTS `organization` (
    `org_id`    INT             NOT NULL,
    `org_name`  VARCHAR(100)    NOT NULL,
    PRIMARY KEY (org_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `book` (
    `book_id`               INT             NOT NULL,
    `isbn`                  VARCHAR(50),
    `book_name`             VARCHAR(100)    NOT NULL,
    `image_url`             VARCHAR(150)    UNIQUE,
    `publisher_id`          INT,
    `published_dt`          DATETIME,
    `page_count`            INT,
    `dimensions_height`     INT,
    `dimensions_width`      INT,
    `dimensions_thickness`  INT,
    PRIMARY KEY (book_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `author` (
    `author_id`     INT             NOT NULL,
    `author_name`   VARCHAR(100)    NOT NULL,
    PRIMARY KEY (author_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `publisher` (
    `publisher_id`      INT             NOT NULL,
    `publisher_name`    VARCHAR(100)    NOT NULL,
    `publisher_code`    VARCHAR(10),
    PRIMARY KEY (publisher_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;


CREATE TABLE IF NOT EXISTS `genre` (
    `org_id`            INT             NOT NULL,
    `genre_id`          INT             NOT NULL,
    `parent_genre_id`   INT,
    `genre_name`        VARCHAR(100)    NOT NULL,
    `sort_key`          VARCHAR(100)    NOT NULL,
    PRIMARY KEY (org_id, genre_id),
    UNIQUE (org_id, sort_key)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `classification` (
    `org_id`            INT             NOT NULL,
    `genre_id`          INT             NOT NULL,
    `book_id`           INT             NOT NULL,
    PRIMARY KEY (org_id, genre_id, book_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;


CREATE TABLE IF NOT EXISTS `collection` (
    `org_id`            INT             NOT NULL,
    `book_id`           INT             NOT NULL,
    `num_of_same_books` INT             NOT NULL,
    `description`       VARCHAR(1000),
    `added_dt`          DATETIME        NOT NULL,
    PRIMARY KEY (org_id, book_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;


CREATE TABLE IF NOT EXISTS `member` (
    `org_id`            INT             NOT NULL,
    `member_id`         INT             NOT NULL,
    `password_hashed`   VARCHAR(512)    NOT NULL,
    `member_name`       VARCHAR(100)    NOT NULL,
    `member_code`       VARCHAR(20)     NOT NULL,
    `is_admin`          BOOLEAN         NOT NULL DEFAULT FALSE,
    `is_enabled`        BOOLEAN         NOT NULL DEFAULT TRUE,
    PRIMARY KEY (org_id, member_id),
    UNIQUE (org_id, member_code)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `borrowed_history` (
    `org_id`            INT             NOT NULL,
    `book_id`           INT             NOT NULL,
    `member_id`         INT             NOT NULL,
    `borrow_times`      INT             NOT NULL,
    `borrowed_dt`       DATETIME        NOT NULL,
    `returned_dt`       DATETIME,
    PRIMARY KEY (org_id, book_id, member_id, borrow_times)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `book_note` (
    `note_id`           INT             NOT NULL,
    `org_id`            INT             NOT NULL,
    `book_id`           INT             NOT NULL,
    `member_id`         INT             NOT NULL,
    `noted_dt`          DATETIME        NOT NULL,
    `note`              VARCHAR(2000)   NOT NULL,
    PRIMARY KEY (note_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;


CREATE TABLE IF NOT EXISTS `writing` (
    `book_id`           INT             NOT NULL,
    `author_id`         INT             NOT NULL,
    PRIMARY KEY (book_id, author_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;



