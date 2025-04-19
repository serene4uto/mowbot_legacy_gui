import yaml



def main():
    
    with open("/workspaces/mowbot_legacy_gui/test/default_params.yaml", "r") as file:
        data = yaml.safe_load(file)
        # print(data)
    

if __name__ == "__main__":
    main()