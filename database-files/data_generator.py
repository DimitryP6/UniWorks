from simple_ddl_parser import DDLParser
from faker import Faker
from faker.providers import BaseProvider
from collections.abc import Callable
import random


## Define the input and output file names.
DDL_FILE_NAME : str = "01_uniworks_ddl.sql"
DML_FILE_NAME : str = "02_uniworks_dml.sql"
## Minimum row counts for table types.
STRONG_ENTITY_MIN : int = 30
MULTIVALUE_MIN : int = 40
WEAK_ENTITY_MIN : int = 50
JUNCTION_TABLE_MIN: int = 125

EXPECTED_DATABASE_NAME : str = "UniWorks"
## The below represents the expected table names, and then their associated row counts,
## which is based off table type (junction, weak entity, etc.). Sorted topologically.
EXPECTED_TABLE_NAMES : dict[str : int] = {
    "users" :  STRONG_ENTITY_MIN,
    "admins" : STRONG_ENTITY_MIN,
    "job_seekers" : STRONG_ENTITY_MIN,
    "job_posters" : STRONG_ENTITY_MIN,
    "company_websites" : MULTIVALUE_MIN,
    "resumes" : STRONG_ENTITY_MIN,
    "personal_websites" : MULTIVALUE_MIN,
    "system_logs" : STRONG_ENTITY_MIN,
    "job_posts" : STRONG_ENTITY_MIN,
    "job_links" : MULTIVALUE_MIN,
    "job_limits" : STRONG_ENTITY_MIN,
    "applications" : STRONG_ENTITY_MIN,
    "activities" : STRONG_ENTITY_MIN,
    "data_reports" : STRONG_ENTITY_MIN,
    "application_reports" : JUNCTION_TABLE_MIN
}

fake : Faker = Faker()

## Custom value provider for certain attributes values that faker doesn't offer.
class UniWorksProvider(BaseProvider):
    def admin_role(self):
        return self.random_element(["College Administrator", "Backend Engineer", "Frontend Engineer", "IT Employee"])
    def major(self):
        return self.random_element(["Chemistry", "Mechanical Engineering", "Electrical Engineering", "Art", "History", 
        "Mathematics", "Data Science", "Computer Scinece", "French Literature", "Computer Engineering"])
    def college(self):
        return self.random_element(["College of Science", "College of Engineering", "College of Computer Science"])
    def error_code(self):
        return "UniWorks Provider Error"
fake.add_provider(UniWorksProvider)

## Connects attribute name types to their callable fake data functions.
ATTRIBUTE_TYPES = {
    # miscellaneous (multiple use these)
    "website" :         lambda: f"'{fake.url()}'",
    "link" :            lambda: f"'{fake.url()}'",
    "city_state" :      lambda: f"'{fake.city()}/{fake.state_abbr()}'",
    "university" :      lambda: f"'{fake.last_name()} University'",
    # users
    "email" :           lambda: f"'{fake.unique.email()}'",
    "password" :        lambda: f"'{fake.password()}'",
    "full_name" :       lambda: f"'{fake.name()}'",
    # admins
    "role" :            lambda: f"'{fake.admin_role()}'",
    # job_seekers
    "major" :           lambda: f"'{fake.major()}'",
    "picture" :         lambda: f"'{fake.image_url()}'",
    "phone" :           lambda: f"'{fake.phone_number()}'",
    "graduation_year" : lambda: f"'{fake.date_between(start_date = "-1y", end_date = "+4y")}'",
    # job_posters
    "company" :         lambda: f"'{fake.company()}'",
    "industry" :        lambda: f"'{fake.bs()}'",
    # resumes
    "education" :       lambda: f"'{fake.paragraph()}'",
    "experience" :      lambda: f"'{fake.paragraph()}'",
    "project" :         lambda: f"'{fake.paragraph()}'",
    "hobby" :           lambda: f"'{fake.paragraph()}'",
    # system_logs
    "error_code" :      lambda: f"'{fake.error_code()}'",
    "error_desc" :      lambda: f"'{fake.sentence()}'",
    "resolved_at" :     lambda: f"'{fake.date_between(start_date='-1y', end_date='today')}'",
    # job_posts
    "job_title" :       lambda: f"'{fake.job()}'",
    "salary" :          lambda: str(round(random.uniform(18, 35), 2)),
    "job_desc" :        lambda: f"'{fake.paragraph()}'",
    # job_limits
    "max_count" :       lambda: str(random.randint(1, 50)),
    "college" :         lambda: f"'{fake.last_name()} College'",
    "min_gpa" :         lambda: str(round(random.uniform(0.0, 4.0), 2)),
    # applications
    "cover_letter" :    lambda: f"'{fake.paragraph()}'",
    "application_date" :lambda: f"'{fake.date_between(start_date='-1y', end_date='today')}'",
    # activities
    "activity_date" :   lambda: f"'{fake.date_time().strftime('%Y-%m-%d %H:%M:%S')}'",
    "notes" :           lambda: f"'{fake.sentence()}'",
    # data_reports
    "filter_criteria" : lambda: f"'{fake.sentence()}'",
    "description" :     lambda: f"'{fake.sentence()}'",
}


def fake_val(attribute_type : str) -> Callable[[None], str]:
    """
    Given an attribute type, walks the dictionary of attribute types to find a matching one,
    and returns its function.
    Arguments:
        attribute_type is the attribute_type
    Returns:
        the function for generating fake data for the given attribute type.
    """
    for dict_attr_type, fn in ATTRIBUTE_TYPES.items():
        if dict_attr_type in attribute_type.lower():
            return fn()
    # If nothing matched, throw an error.
    raise ValueError(f"No defined type found for {attribute_type}.")

"""
Parses the DDL file into a dictionary between the table name and its 
associated DDL parser dictionary.
"""
ddl_content : str = open(DDL_FILE_NAME).read()
parsed_ddl : dict[str, dict] = {
    t.get("table_name") : t
    for t in DDLParser(content = ddl_content, silent = False).run(output_mode = "mysql")
    if t.get("primary_key") # Get only parts that could be a MySQL table.
}

## The following list stores the lines for the DML statements.
output_dml_lines : list[str] = [f"USE {EXPECTED_DATABASE_NAME};\n"]

## The following is a dictionary that stores possible primary key values for attributes.
pk_vals : dict[str : list[int]] = {}

## Generates MySQL VALUES (...) rows for each table.
for (table_name, num_rows) in EXPECTED_TABLE_NAMES.items():
    table_info : dict = parsed_ddl[table_name]
    columns : list[dict] = table_info["columns"]
    # Skip columns that are autoincremented or have a default value.
    attrs_to_skip : set[str] = {
        c["name"] for c in columns
        if c.get("autoincrement") == True
        or c.get("default") is not None
    }
    # Construct a dictionary from column to parent tablel name for foreign keys.
    fk_attrs : dict[str : str] = {
        c["name"] : c["references"]["table"].lower()
        for c in columns if c.get("references") is not None
    }
    # Pre-sample without replacement unique foreign key ids.
    unique_fk_samples : dict[str : list[int]] = {}
    for (fk_attr, parent_table_name) in fk_attrs.items():
        if any((c["name"] == fk_attr and c.get("unique") == True) for c in columns):
            unique_fk_samples[fk_attr] = random.sample(pk_vals[parent_table_name], num_rows)
    # Create a list of attributes to not skip.
    attributes_to_add_for_table : list[dict] = [c for c in columns 
                                            if c["name"] not in attrs_to_skip]
    # Create a list of empty strings, where each string is 'col1, col2, col3' for each insertion.
    all_value_lists : list[str] = []
    # Junction table case.
    if num_rows == JUNCTION_TABLE_MIN:
        fk_columns : list[str] = list(fk_attrs.keys())
        fk_parents : list[str] = [fk_attrs[col] for col in fk_columns]
        pairs = random.sample(
            [(a, b) for a in pk_vals[fk_parents[0]] for b in pk_vals[fk_parents[1]]],
            num_rows
        )
        for pair in pairs:
            all_value_lists.append(f"    ({', '.join(str(v) for v in pair)})")
    # Non junction table case.  
    else:
        for row_idx in range(num_rows):
            value_list : list[str] = [] # values for one insertion row.
            for attr in attributes_to_add_for_table:
                if attr["name"] in fk_attrs:
                    parent_table_name : str = fk_attrs[attr["name"]]
                    if attr["name"] in unique_fk_samples:
                        value_list.append(str(unique_fk_samples[attr["name"]][row_idx]))
                    else:
                        value_list.append(str(random.choice(pk_vals[parent_table_name])))
                elif attr["type"].upper() == "ENUM":
                    choice : str = random.choice(attr["values"]).strip("'")
                    value_list.append(f"'{choice}'")
                elif attr["type"].upper() in ("BOOL", "BOOLEAN"):
                    value_list.append(random.choice(['TRUE', 'FALSE']))
                else:
                    value_list.append(fake_val(attr["name"]))
            all_value_lists.append(f"    ({", ".join(value_list)})")
    # Format the rows of the insert statement.
    rows : str = ",\n".join(all_value_lists)
    # Format the attributes as 'col1, col2, ..., coln'.
    column_names : str = ", ".join(c["name"] for c in attributes_to_add_for_table)
    output_dml_lines.append(f"INSERT INTO {table_name} ({column_names}) VALUES\n{rows};\n")
    # Add the generated primary keys, and reset faker.
    pk_vals[table_name] = list(range(1, num_rows + 1))
    fake.unique.clear()

## Write to output DML file.
open(DML_FILE_NAME, "w").write("\n".join(output_dml_lines))