import pandas as pd
import streamlit as st
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

@st.cache
def load_associate_data():
    path = r'\\ant.amazon.com\dept-eu\HAM2\Outbound\public\02_OB Problem Solve\DLMgmt\\'
    filename = 'acanel_performancetracking_mixadj-std_HAM2_60days.dat'
    raw_data = pd.read_csv(path+filename, sep='\t', error_bad_lines=False)
    return raw_data
    #if uploaded_file is not None:
    #df = pd.read_csv(uploaded_file, sep='\t', error_bad_lines=False)
    #return df

def upload_file():
              #\\ant.amazon.com\dept-eu\HAM2\Outbound\public_OB Problem Solve\DLMgmt\acanel_performancetracking_mixadj-std_HAM2_60days.dat

    uploaded_file = st.file_uploader(f"Upload {filename} from -> {path}", type="dat")
    if uploaded_file is not None:
        state = True
        data_load_state = st.text('Loading data...')
        raw_data = load_associate_data(uploaded_file)
        data_load_state.text('Loading data... -> done!')
        return raw_data, state
    else: return None, None

    #path = "//ant/dept-eu/HAM2/Outbound/public/02_OB Problem Solve/DLMgmt/"
    #filename = "acanel_performancetracking_mixadj-std_HAM2_60days.dat"
    #st.write("Cache miss: my_cached_func(load_associate_data) ran")


def show_manager_associates(df, manager):
    df = df[df['l1supervisor']==manager]
    associates = df['employee_name'].unique()
    return associates

def create_associate_df(df, associate_login):
    df_associate = df[df['login_name']==associate_login]
    AA_trend = df_associate.pivot_table(index=['date'], columns='processpath', values='mixadjusted tph', aggfunc='mean')

    AA_DD1 = df_associate.pivot_table(index=['login_name','employee_name'], columns='processpath', values='mixadjusted tph', aggfunc='mean')
    AA_DD = pd.DataFrame()
    AA_DD['UPH'] = AA_DD1.stack()
    #st.write('create_associate_df ran')
    return AA_trend, AA_DD, df_associate

def create_deepdive_chart(AA_trend, AA_DD, df_associate, associate, processpath, BM_Rates, max_UPH):
    # Setting up the fig and axes
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=[18,8])

    if 'UNKNOWN' in AA_DD.index:
        AA_DD = AA_DD.drop('UNKNOWN', axis=0)
    else: pass

    if 'UNKNOWN' in AA_trend.columns:
        AA_trend = AA_trend.drop('UNKNOWN', axis=1)
    else: pass


    # Plotting to ax1 and ax2
    AA_DD.plot(kind='bar', ax=ax1)
    AA_trend.plot(marker='o', ax=ax2, linestyle='--', zorder=2)

    # Adjusting the axes layout
    #plt.tight_layout()
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.4) # This does the same as tight_layout()

    # Setting ax1 parameters
    ax1.set_title(str(df_associate.iloc[0,2]+' ('+associate+')\n Last 60 days ('+str(len(AA_trend))+' observations)\n'), fontsize=16, fontweight='regular')
    ax1.set_xticklabels(ax1.get_xticklabels(),rotation=0, fontsize='14', fontweight='regular')
    ax1.xaxis.label.set_visible(False) # Hide the x-axis label

    # Setting ax2 parameters
    ax2.set_title(str(df_associate.iloc[0,2])+' ('+associate+')\n Last 60 days ('+str(len(AA_trend))+' observations)\nBenchmark = '+processpath, fontsize=16, fontweight='regular')
    ax2.set_ylim(0, max_UPH)
    ax2.axhline(y=BM_Rates[processpath], linestyle='-', color='red', zorder=1)
    ax2.set_xticklabels(ax2.get_xticklabels(),rotation=0)
    ax2.xaxis.label.set_visible(False) # Hide the x-axis label
    #plt.savefig(str(associate)+'.png',bbox_inches='tight') # Activate when you want to save the image file

    # Call the function above. All the magic happens there.
    add_value_labels(ax1,5)

    return fig

def add_value_labels(ax, spacing=5):
    """Add labels to the end of each bar in a bar chart.

    Arguments:
        ax (matplotlib.axes.Axes): The matplotlib object containing the axes
            of the plot to annotate.
        spacing (int): The distance between the labels and the bars.
    """

    # For each bar: Place a label
    for rect in ax.patches:
        # Get X and Y placement of label from rect.
        y_value = rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2

        # Number of points between bar and label. Change to your liking.
        space = spacing
        # Vertical alignment for positive values
        va = 'bottom'

        # If value of bar is negative: Place label below bar
        if y_value < 0:
            # Invert space to place label below
            space *= -1
            # Vertically align label at top
            va = 'top'

        # Use Y value as label and format number with zero decimal places
        label = "{:.0f}".format(y_value)

        # Create annotation
        ax.annotate(
            label,                      # Use `label` as label
            (x_value, y_value),         # Place label at end of the bar
            xytext=(0, space),          # Vertically shift label by `space`
            textcoords="offset points", # Interpret `xytext` as offset in points
            ha='center',                # Horizontally center label
            va=va)                      # Vertically align label differently for
                                        # positive and negative values.

def create_line_chart(AA_trend):
    if 'UNKNOWN' in AA_trend.columns:
        AA_trend = AA_trend.drop(columns='UNKNOWN')
    melted_df = pd.melt(AA_trend.reset_index(),'date',var_name='process_path', value_name='UPH')
    melted_df['date']= pd.to_datetime(melted_df['date'])
    fig = px.scatter(melted_df, x='date', y='UPH', color='process_path')
    return fig

def create_bar_chart(AA_DD):
    mean_tidy = AA_DD.reset_index()[['processpath','UPH']]
    fig = px.bar(mean_tidy, x='processpath', y='UPH', color='processpath')
    return fig

# Constant Values

processpaths = ('Stow', 'Pick', 'Each Receive', 'Decant', 'Prep', 'Pack SM', 'Pack Chuting', 'Rebin', 'Induct', 'Pack No Slam','UNKNOWN') # Process Paths
BM_Rates = {'Stow':265, 'Pick':308, 'Each Receive':409, 'Decant':1200, 'Prep':147, 'Pack Chuting':245.9, 'Pack SM': 148.9 , 'Rebin': 0, 'Induct': 0, 'Pack No Slam': 0, 'UNKNOWN':0} # Benchmark Rates 2020
max_UPH_dict = {'Stow':450, 'Pick':500, 'Each Receive':600, 'Decant':1800, 'Prep':220, 'Pack Chuting':500, 'Pack SM': 300} # Set max limit here

# Visible page
# ------------

def main():
    st.title("acanel's HAM2 Associate Dashboard")
    st.text("")

    raw_data = load_associate_data()

    # Dashboard Title

    # Checkbox for Raw Data
    #if st.checkbox('Show raw data'):
    #    st.subheader('Raw data')
    #    st.write(raw_data)

    unique_managers = raw_data['l1supervisor'].unique()

    # Select Buttons
    manager = st.sidebar.selectbox('Manager', unique_managers)
    associates = show_manager_associates(raw_data, manager)
    associate_name = st.sidebar.selectbox('Associate', associates)
    #processpath = st.sidebar.selectbox('Process Path', processpaths)
    #max_UPH = max_UPH_dict[processpath]
    #st.sidebar.markdown(f'Benchmark for {processpath}: {BM_Rates[processpath]}')

    # Calculate based on Buttons
    associate_login = raw_data['login_name'][raw_data['employee_name']==associate_name].iloc[0]
    associates = show_manager_associates(raw_data, manager)

    # Write Info
    st.sidebar.markdown(f'Associate Login: {associate_login}')
    #st.write(f'Associates of {manager}:')
    #st.write(associates)

    # Show Associate Deep Dive
    AA_trend, AA_DD, df_associate = create_associate_df(raw_data, associate_login)
    mean_UPH = AA_DD.reset_index().set_index('processpath')['UPH']
    st.text("")
    #st.bar_chart(mean_UPH)
    st.plotly_chart(create_line_chart(AA_trend))
    st.plotly_chart(create_bar_chart(AA_DD))
    #st.pyplot(AA_trend.plot(marker='o', linestyle='--'))
    # Display Chart
    #try:
    #    st.pyplot(create_deepdive_chart(AA_trend, AA_DD, df_associate, associate_name, processpath, BM_Rates, max_UPH))
    #except: st.warning("No Data")

    #Show Deep Dive Tables
    st.write(AA_trend)
    st.write(AA_DD)

if __name__ == '__main__':
    main()
