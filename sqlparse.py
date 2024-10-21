import sqlparse
import re

line = '''
CREATE TABLE public.actor (
    actor_id integer DEFAULT nextval('public.actor_actor_id_seq'::regclass) NOT NULL,
    first_name character varying(45) NOT NULL,
    last_name character varying(45) NOT NULL,
    last_update timestamp without time zone DEFAULT now() NOT NULL
);

CREATE TABLE `Employee` ( `Emp_ID` VARCHAR(20) NOT NULL ,`Name` VARCHAR(50) NOT NULL ,  
`Age` INT NOT NULL ,`Phone_No` VARCHAR(10) NOT NULL ,`Address` VARCHAR(100) NOT NULL ,
 PRIMARY KEY (`Emp_ID`));
 
 CREATE TABLE Persons (
    Personid int IDENTITY(1,1) PRIMARY KEY,
    LastName varchar(255) NOT NULL,
    FirstName varchar(255),
    Age int
);

CREATE TABLE Ofrders (
    OrderID int  PRIMARY KEY IDENTITY(10,25),
    Orders int FOREIGN KEY IDENTITY(5,3),
    LastName varchar(255) NOT NULL,
    FirstName varchar(255),
    Age int
);

CREATE TABLE public.category (
    category_id integer DEFAULT nextval('public.category_category_id_seq'::regclass) NOT NULL,
    name character varying(25) NOT NULL,
    last_update timestamp without time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS "sample_schema"."sample_table"
(
    "div_cd" VARCHAR(2) NOT NULL
    ,"div_name" VARCHAR(30) NOT NULL
    ,"org_cd" VARCHAR(8) NOT NULL
    ,"org_name" VARCHAR(60) NOT NULL
    ,"team_cd" VARCHAR(2) NOT NULL
    ,"team_name" VARCHAR(120) NOT NULL
    ,"personal_cd" VARCHAR(7) NOT NULL
    ,"personal_name" VARCHAR(300) NOT NULL
    ,"username" VARCHAR(6) NOT NULL
    ,"staff_flg" CHAR(1)  DEFAULT '0'::bpchar ENCODE lzo
    ,"leader_flg" CHAR(1)  DEFAULT '0'::bpchar ENCODE lzo
)
DISTSTYLE EVEN
;

CREATE TABLE IF NOT EXISTS "sample_schema"."ref_table"
(
     "staff_flg" CHAR(1)  DEFAULT '0'::bpchar SORTKEY ENCODE lzo 
    ,"leader_flg" CHAR(1)  DEFAULT '0'::bpchar ENCODE lzo
)
DISTSTYLE EVEN
;
'''


def shift_foreign_key_to_end(sql_statement):
    # Split the statement into words
    words = sql_statement.split()

    # Find the index of 'FOREIGN' and 'KEY'
    foreign_index = words.index('FOREIGN')
    key_index = words.index('KEY')

    # Extract 'FOREIGN KEY' and remove from the list
    foreign_key = words[foreign_index:key_index + 1]
    del words[foreign_index:key_index + 1]

    # Append 'PRIMARY KEY' to the end
    words.extend(foreign_key)

    # Join the words back into a string
    return ' '.join(words)


def shift_primary_key_to_end(sql_statement):
    # Split the statement into words
    words = sql_statement.split()

    # Find the index of 'PRIMARY' and 'KEY'
    primary_index = words.index('PRIMARY')
    key_index = words.index('KEY')

    # Extract 'PRIMARY KEY' and remove from the list
    primary_key = words[primary_index:key_index + 1]
    del words[primary_index:key_index + 1]

    # Append 'PRIMARY KEY' to the end
    words.extend(primary_key)

    # Join the words back into a string
    return ' '.join(words)


def get_table_name(tokens):
    for token in reversed(tokens):
        if token.ttype is None:
            return token.value
    return " "


parse = sqlparse.parse(line)
# print(parse)
for stmt in parse:
    # print(stmt)
    # print(stmt.tokens)
    # Get all the tokens except whitespaces
    tokens = [t for t in sqlparse.sql.TokenList(stmt.tokens) if t.ttype != sqlparse.tokens.Whitespace]
    is_create_stmt = False
    for i, token in enumerate(tokens):
        # Is it a create statements ?
        if token.match(sqlparse.tokens.DDL, 'CREATE'):
            is_create_stmt = True
            continue

        # If it was a create statement and the current token starts with "("
        if is_create_stmt and token.value.startswith("("):
            # Get the table name by looking at the tokens in reverse order till you find
            # a token with None type
            print(f"table: {get_table_name(tokens[:i])}")

            # Now parse the columns
            txt = token.value

            columns_alt = txt[1:txt.rfind(")")].replace("\n", "")
            # print(columns_alt)
            if columns_alt.find("IDENTITY") != -1:
                columns_alt = re.sub(r'IDENTITY\((\d+),(\d+)\)', r'IDENTITY(\1:\2)', columns_alt)

            columns = columns_alt.split(",")
            for column in columns:
                if column.find("PRIMARY") != -1:
                    column = shift_primary_key_to_end(column)
                elif column.find("FOREIGN") != -1:
                    column = shift_foreign_key_to_end(column)

                c = ' '.join(column.split()).split()
                #print("value of c")
                #print(c)
                #print(len(c))
                c_name = c[0].replace('\"', "")
                c_type = c[1]  # For condensed type information
                # OR
                # c_type = " ".join(c[1:]) # For detailed type information
                print(f"column: {c_name}")
                print(f"date type: {c_type}")
                if len(c) >= 5:
                    if c[3] == "PRIMARY" and c[4] == "KEY":
                        print("PRIMARY KEY Constraint")
                    if c[3] == "FOREIGN" and c[4] == "KEY":
                        print("FOREIGN KEY Constraint")
                    if c[3] == "NOT" and c[4] == "NULL":
                        print("NOT NULL constraint")
                elif len(c) >= 4:
                    if c[2] == "PRIMARY" and c[3] == "KEY":
                        print("PRIMARY KEY Constraint")
                    if c[2] == "FOREIGN" and c[3] == "KEY":
                        print("FOREIGN KEY Constraint")
                    if c[2] == "NOT" and c[3] == "NULL":
                        print("NOT NULL constraint")
                elif len(c) >= 3:
                    if c[2] == "NULL" or c[2] == "NULLABLE":
                        print(" NULL allowed")

            print("---" * 20)
            break
