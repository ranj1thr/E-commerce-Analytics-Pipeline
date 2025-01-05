import pandas as pd
from sqlalchemy import create_engine, text
import os
import logging
import hashlib
import warnings
from tabulate import tabulate
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import pytz
from datetime import datetime

# Suppress openpyxl warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# Rich console for better output display
console = Console()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Folder paths containing the files
flipkart_folder = r"C:\Users\Ranji\OneDrive - MSFT\Shakedeal Documents\Report Files\Flipkart"
amazon_folder = r"C:\Users\Ranji\OneDrive - MSFT\Shakedeal Documents\Report Files\Amazon"

# Connect to PostgreSQL
engine = create_engine("postgresql://postgres:2705@localhost:5432/Shakedeal")

# Function to check if table exists (handles case sensitivity)
def table_exists(table_name, engine):
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = LOWER('{table_name}')
                OR table_name = '{table_name}'
            );
        """))
        return result.scalar()

# Function to create table dynamically based on DataFrame columns
def create_table_dynamically(df, table_name, engine):
    column_definitions = ", ".join([f'"{col}" TEXT' for col in df.columns])
    # Add 'month' and 'unique_id' only if they're not already in the DataFrame
    if 'month' not in df.columns:
        column_definitions += ', "month" TEXT'
    if 'unique_id' not in df.columns:
        column_definitions += ', "unique_id" TEXT UNIQUE'
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        {column_definitions}
    );
    """
    with engine.begin() as conn:
        conn.execute(text(create_table_query))
        console.log(f"[green]Table '{table_name}' created dynamically based on file columns (if it didn't exist).[/green]")

# Function to add missing columns dynamically
def add_missing_columns(df, table_name, engine):
    for col in df.columns:
        try:
            with engine.begin() as conn:
                alter_query = f'ALTER TABLE "{table_name}" ADD COLUMN "{col}" TEXT;'
                conn.execute(text(alter_query))
                console.log(f"[cyan]Added missing column: '{col}' to table '{table_name}'.[/cyan]")
        except Exception as e:
            if 'already exists' not in str(e).lower():
                console.log(f"[red]Error adding column '{col}' to table '{table_name}': {e}[/red]")

    # Add 'month' column if missing
    try:
        with engine.begin() as conn:
            conn.execute(text(f'ALTER TABLE "{table_name}" ADD COLUMN "month" TEXT;'))
            console.log(f"[cyan]Added missing column: 'month' to table '{table_name}'.[/cyan]")
    except Exception as e:
        if 'already exists' not in str(e).lower():
            console.log(f"[red]Error adding column 'month' to table '{table_name}': {e}[/red]")

# Function to generate unique ID
def generate_unique_id(row):
    row_string = "_".join([str(row[col]) for col in row.index if col != 'unique_id'])
    return hashlib.sha256(row_string.encode()).hexdigest()

# Function to extract Month from Date Columns
def extract_month(df, source):
    if source.lower() == "amazon" and 'purchase-date' in df.columns:
        df['month'] = pd.to_datetime(df['purchase-date'], errors='coerce').dt.strftime('%B')
    elif source.lower() == "flipkart" and 'order_date' in df.columns:
        df['month'] = pd.to_datetime(df['order_date'], errors='coerce').dt.strftime('%B')
    else:
        console.log("[yellow]No date column found for month extraction.[/yellow]")
    return df

# Function to convert a date column to IST timezone
def convert_to_ist(date_column):
    utc = pytz.UTC
    ist = pytz.timezone('Asia/Kolkata')
    def convert_to_ist_single(x):
        if pd.notnull(x):
            if x.tzinfo is None:  # Naive datetime
                return utc.localize(x).astimezone(ist)
            else:  # Aware datetime
                return x.astimezone(ist)
        return x
    return date_column.apply(convert_to_ist_single)

# Function to process a single file
def process_file(file_path, source, summary_logs):
    try:
        # Load file into a DataFrame
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.txt'):
            df = pd.read_csv(file_path, delimiter="\t")
        else:
            console.log("[red]Unsupported file format.[/red]")
            return

        # Sanitize column names
        df.columns = df.columns.str.replace(' ', '_').str.lower()

        # Convert purchase-date to IST if Amazon
        if source.lower() == "amazon" and 'purchase-date' in df.columns:
            df['purchase-date'] = pd.to_datetime(df['purchase-date'], errors='coerce')  # Ensure it's a datetime object
            df['purchase-date'] = convert_to_ist(df['purchase-date'])
            console.log("[blue]Converted 'purchase-date' to IST.[/blue]")

        # Extract Month Column
        df = extract_month(df, source)

        # Set table name dynamically
        table_name = "AZ_Sales_Report" if "amazon" in source.lower() else "FK_Sales_Report"
        console.print(f"[bold blue]Processing File: {os.path.basename(file_path)} -> Table: {table_name}[/bold blue]")

        # Check if table exists; if not, create it dynamically
        if not table_exists(table_name, engine):
            create_table_dynamically(df, table_name, engine)
        else:
            add_missing_columns(df, table_name, engine)

        # Generate unique_id for each row
        df['unique_id'] = df.apply(generate_unique_id, axis=1)

        # Fetch existing unique_ids from the database
        with engine.connect() as conn:
            existing_ids = set(pd.read_sql(f'SELECT unique_id FROM "{table_name}";', conn)['unique_id'].tolist())
        console.log(f"[magenta]Retrieved {len(existing_ids)} existing unique IDs from the database.[/magenta]")

        # Filter out duplicates
        new_data = df[~df['unique_id'].isin(existing_ids)].drop_duplicates(subset=['unique_id'])

        # Insert new data into the table
        rows_inserted = len(new_data)
        if rows_inserted > 0:
            new_data.to_sql(table_name, engine, if_exists="append", index=False, chunksize=1000)
            console.print(f"[green]✔ {os.path.basename(file_path)}: {rows_inserted} rows inserted successfully.[/green]")
        else:
            console.print(f"[yellow]⚠ {os.path.basename(file_path)}: No new data to insert.[/yellow]")

        # Append to summary log
        summary_logs.append({
            "File Name": os.path.basename(file_path),
            "Table Name": table_name,
            "Rows Inserted": rows_inserted,
            "Status": "Success" if rows_inserted > 0 else "No New Data"
        })

    except Exception as e:
        console.print(f"[red]✘ {os.path.basename(file_path)}: An error occurred: {e}[/red]")
        summary_logs.append({
            "File Name": os.path.basename(file_path),
            "Table Name": table_name,
            "Rows Inserted": 0,
            "Status": f"Error: {str(e)}"
        })

# User Input for Platform and Multiple Files
platform = input("Enter platform (Amazon/Flipkart): ").strip().lower()
if platform == "amazon":
    folder = amazon_folder
    source = "Amazon"
elif platform == "flipkart":
    folder = flipkart_folder
    source = "Flipkart"
else:
    console.print("[red]Invalid platform. Please enter 'Amazon' or 'Flipkart'.[/red]")
    exit()

# List available files in the folder and ask for file names
available_files = [f for f in os.listdir(folder) if f.endswith(('.xlsx', '.csv', '.txt'))]
console.print("[cyan]\nAvailable Files:[/cyan]")
for idx, file in enumerate(available_files, start=1):
    console.print(f"{idx}. {file}")

file_indices = input("Enter file numbers (comma-separated) to process: ").strip().split(",")
try:
    file_paths = [os.path.join(folder, available_files[int(i) - 1].strip()) for i in file_indices]
except (IndexError, ValueError):
    console.print("[red]Invalid input. Please enter valid file numbers.[/red]")
    exit()

# Initialize summary logs
summary_logs = []

# Simplified Progress Display
with Progress(console=console) as progress:
    task = progress.add_task("[cyan]Processing Files...", total=len(file_paths))
    for idx, file_path in enumerate(file_paths, start=1):
        console.print(f"[bold blue]({idx}/{len(file_paths)}) Processing File: {os.path.basename(file_path)}[/bold blue]")
        if os.path.exists(file_path):
            process_file(file_path, source, summary_logs)
        else:
            console.log(f"[red]File '{file_path}' not found in {folder}.[/red]")
        progress.advance(task)

# Display combined summary table
console.print(f"\n[bold cyan]Final Processing Summary for {source}:[/bold cyan]")
summary_table = Table(show_header=True, header_style="bold blue")
summary_table.add_column("File Name")
summary_table.add_column("Table Name")
summary_table.add_column("Rows Inserted", justify="right")
summary_table.add_column("Status")

for log in summary_logs:
    summary_table.add_row(log["File Name"], log["Table Name"], str(log["Rows Inserted"]), log["Status"])

console.print(summary_table)
 