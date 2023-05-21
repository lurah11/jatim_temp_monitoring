from airflow import DAG 
from datetime import datetime, timedelta
from airflow.decorators import task 




with DAG(start_date=datetime(2023,5,22), dag_id="test_etl_bmkg", schedule_interval='0 14 * * *') as dag:

    @task.external_python(task_id="download_bmkg_xml",python='/home/lurah11/sinau/Tetris/capstone/temp_env/bin/python',retry_delay=timedelta(minutes=30),retries=50)
    def download():
        from datetime import datetime, timedelta
        import requests 


        def get_filename() : 
            today = datetime.now().date()
            filename = today.strftime("bmkg-%Y%m%d.xml")
            return filename
        dataset_dir = '/home/lurah11/sinau/Tetris/capstone/jatim_temp_monitoring/supp_datasets'

        
        try : 
            print("agus1")
            filename = get_filename()
            bmkg = requests.get('https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-JawaTimur.xml')
            # bmkg = requests.get('https://thisisfictiouswebsite.com')
            bmkg.raise_for_status()
            with open(f"{dataset_dir}/{filename}",'wb') as f:
                f.write(bmkg.content)
                print(f"successfully write--{filename}")
        except requests.exceptions.HTTPError as errh:
            print("Error fetching data")
            
    
    @task.external_python(task_id="ETL_w_DJANGO",python='/home/lurah11/sinau/Tetris/capstone/temp_env/bin/python')
    def etl_django():
        import os
        import sys
        import pandas as pd
        from datetime import datetime

        def get_filename() : 
            today = datetime.now().date()
            filename = today.strftime("bmkg-%Y%m%d.xml")
            return filename

        d = get_filename()
        
        base_dir = os.path.dirname('/home/lurah11/sinau/Tetris/capstone/jatim_temp_monitoring/temperature')
        project = os.path.basename('/home/lurah11/sinau/Tetris/capstone/jatim_temp_monitoring/temperature')
        dataset_dir = '/home/lurah11/sinau/Tetris/capstone/jatim_temp_monitoring/supp_datasets'
        sys.path.append(base_dir)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{project}.settings")

        import django 
        django.setup()
        import pandas as pd 
        from temp.models import Temp 
        from bs4 import BeautifulSoup
        from datetime import datetime
        from temp.models import City 


        def get_temp_hum_data(area,index,target_date): 
            my_dict = {}
            my_dict['tmax'] = area.select(f'parameter[id="tmax"] timerange[day="{target_date}"] value[unit="C"]')[0].text
            my_dict['tmin'] = area.select(f'parameter[id="tmin"] timerange[day="{target_date}"] value[unit="C"]')[0].text
            my_dict['humax'] = area.select(f'parameter[id="humax"] timerange[day="{target_date}"] value')[0].text
            my_dict['humin'] = area.select(f'parameter[id="humin"] timerange[day="{target_date}"] value')[0].text
            df = pd.DataFrame(my_dict,index=[index])
            return df 

        def get_area_detail(area,index,target_date): 
            area_dict = {}
            attributes = area.attrs
            area_dict['date'] = target_date
            area_dict['id'] = attributes.get('id')
            area_dict['name']=area.select('name')[1]
            area_dict['latitude'] = attributes.get('latitude')
            area_dict['longitude'] = attributes.get('longitude')
            df = pd.DataFrame(area_dict, index=[index])
            return df
            

        def get_t_hum_monitoring_data(bmkg,last_date): 
            areas = bmkg.select('area[type="land"]')
            res_df = pd.DataFrame()
            for i,area in enumerate(areas) : 
                res_detail = get_temp_hum_data(area,i,last_date)
                area_detail = get_area_detail(area,i,last_date)
                if not res_df.empty: 
                    df = pd.concat((area_detail,res_detail),axis=1)
                    res_df = pd.concat((res_df,df))
                else : 
                    df = pd.concat((area_detail,res_detail),axis=1)
                    res_df = df
            return res_df


        def read_xml(d): 
                with open(f"{dataset_dir}/{d}") as xml : 
                    date_obj = datetime.strptime(d,"bmkg-%Y%m%d.xml").date()
                    last_date = date_obj.strftime("%Y%m%d")
                    bs = BeautifulSoup(xml,features="xml")
                    new_data = get_t_hum_monitoring_data(bs,last_date)
                return (new_data,date_obj)

        def load_data(d):  #date -> 1 , name -> 3, tmax->6 , tmin->7, humax->8, humin->9
            df,date_obj = read_xml(d)
            for data in df.itertuples(): 
                print(f"{data[1]}--{data[3]}--{data[6]}")
                city = City.objects.get(name=data[3])
                Temp.objects.create(city=city,date=date_obj,tmax=data[6],tmin=data[7],humax=data[8],humin=data[9])
            print("data has been loaded into DB")

        return load_data(d)
    



    download() >> etl_django()


