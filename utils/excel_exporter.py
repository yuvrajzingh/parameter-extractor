import pandas as pd

def generate_excel(parameters, file_path):
    if not parameters:
        print("No parameters to write to Excel.")
        return  

    
    data_dict = {}
    for param in parameters:
        if param['name'] not in data_dict:
            data_dict[param['name']] = []
        data_dict[param['name']].append(param['value'])

    
    # max_len = max(len(values) for values in data_dict.values())
    # for key, values in data_dict.items():
    #     values.extend([''] * (max_len - len(values)))

    print("data_dict :", data_dict)

    df = pd.DataFrame(data_dict)
    df.to_excel(file_path, index=False)












