import yaml

pricing = yaml.load(open("config/pricing.yaml"), Loader=yaml.FullLoader)
general = yaml.load(open("config/general.yaml"), Loader=yaml.FullLoader)

