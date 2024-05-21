import streamlit as st
import pandas as pd
import sqlalchemy
from io import StringIO
import streamlit.components.v1 as components
import plotly.express as px

# Connection string to the PostgreSQL database
DATABASE_URL = "postgresql+psycopg2://user:password@postgres:5432/datascience"
# DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/datascience"

# Setup database connection
@st.cache_resource
def get_database_connection():
    engine = sqlalchemy.create_engine(DATABASE_URL)
    return engine.connect()

# Fetch dataset names from the database
@st.cache_data
def get_datasets(_conn):
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    return pd.read_sql(query, _conn)

# Fetch metadata for a specific table
@st.cache_data
def get_table_description(_conn, table_name):
    query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
    return pd.read_sql(query, _conn)

# Load data from a specific table
@st.cache_data
def load_data(_conn, table_name):
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, _conn)

def main():
    # ตั้งค่า CSS สำหรับสีพื้นหลัง
    page_bg_img = """
    <style>
    [data-testid="stAppViewContainer"] {
    background-color: #FFCCCC;
    }
    [data-testid="stSidebar"] {
    background-color: #DDA0DD;
    }
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

    conn = get_database_connection()
    datasets = get_datasets(conn)
    dataset_names = datasets['table_name'].tolist()

    if not dataset_names:
        st.error("No datasets found in the database.")
        return

    dataset_selected = st.sidebar.selectbox("Select a dataset", dataset_names)

    if dataset_selected:
        # แสดงชื่อ dataset ที่ถูกเลือก
        st.title(f"{dataset_selected}")

        # Display metadata
        metadata = get_table_description(conn, dataset_selected)
        if not metadata.empty:
            st.write(f"Metadata for {dataset_selected}:")
            st.dataframe(metadata)
        else:
            st.write("No metadata available.")

        # Load and display data
        data = load_data(conn, dataset_selected)
        if not data.empty:
            st.write("Data Preview:")
            st.dataframe(data, height=400)  # กำหนดความสูงของตารางเป็น 400 พิกเซล

            # Basic EDA options
            if st.button("Show Info"):
                buffer = StringIO()
                data.info(buf=buffer)
                s = buffer.getvalue()
                st.text(s)

            if st.button("Show Distribution"):
                st.write(data.describe())

            # เพิ่มปุ่มสำหรับการสร้างกราฟและการแสดง Visualization
            st.write("## Visualization")

            # Chart type selection
            chart_type = st.selectbox("Select the chart type", ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Histogram", "Box Plot"])

            # Column selection for x and y axes
            columns = data.columns.tolist()
            x_column = st.selectbox("Select the X-axis column", columns)
            y_column = st.selectbox("Select the Y-axis column", columns) if chart_type != "Pie Chart" else None

            if x_column and (y_column or chart_type == "Pie Chart"):
                if chart_type == "Bar Chart":
                    fig = px.bar(data, x=x_column, y=y_column, title=f"Bar Chart of {x_column} vs {y_column}")
                elif chart_type == "Line Chart":
                    fig = px.line(data, x=x_column, y=y_column, title=f"Line Chart of {x_column} vs {y_column}")
                elif chart_type == "Scatter Plot":
                    fig = px.scatter(data, x=x_column, y=y_column, title=f"Scatter Plot of {x_column} vs {y_column}")
                elif chart_type == "Pie Chart":
                    fig = px.pie(data, names=x_column, title=f"Pie Chart of {x_column}")
                elif chart_type == "Histogram":
                    fig = px.histogram(data, x=x_column, title=f"Histogram of {x_column}")
                elif chart_type == "Box Plot":
                    fig = px.box(data, x=x_column, y=y_column, title=f"Box Plot of {x_column} vs {y_column}")
                
                st.plotly_chart(fig)

            group_members = [
                "นายธีรวิสิทธ์ จินนารัตน์           เลขทะเบียน 6424650312",
                "นายรัชตะ หมื่นรัตน์                   เลขทะเบียน 6424650361",
                "นายวิชัย มาเจริญ                       เลขทะเบียน 6424650379",
                "นายศิวกร นิตย์กิจสมบูรณ์       เลขทะเบียน 6424650395",
                "นายอธิชา เจริญธนกิจกุล        เลขทะเบียน  6424650494"
            ]
            
            # แสดงรายชื่อสมาชิกของกลุ่ม
            if st.button("Group Members"):
                st.dataframe(group_members)

        else:
            st.write("No data available for this dataset.")

# Components Bootstrap
st.subheader("กลุ่มบ้านเช่า")
components.html(
    """
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
<style>
    .card-img-top {
        object-fit: cover;
        height: 450px;
        width: 800px;
    }
</style>
<div class="card" style="width: 18rem;">
  <img class="card-img-top" src="https://ca-times.brightspotcdn.com/dims4/default/fdaa77f/2147483647/strip/true/crop/3000x2051+0+0/resize/1200x820!/quality/75/?url=https%3A%2F%2Fcalifornia-times-brightspot.s3.amazonaws.com%2F5c%2F94%2F6be072a140cba6d21278a005c540%2Fmmpr-y1-104c-l.jpg" alt="Card image cap">
</div>
""",
    height=450,
    width=800
)

if __name__ == "__main__":
    main()
