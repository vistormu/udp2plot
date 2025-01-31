# from udp to a real-time plot

this small python util is for plotting time-series data from a udp stream.

simply modify the config.toml file to match your needs and run the script.

## installation

clone the repository and install the dependencies with pip:

```bash
git clone https://github.com/vistormu/udp2plot.git
cd udp2plot
```

```bash
pip install -r requirements.txt
```

> [!NOTE]
> this script requires python 3.10 or higher

## usage

modify the config.toml file to match your needs

if you want to specify the path of the config file, you can do so by passing the path as an argument:

```bash
python main.py --config path/to/config.toml
```

## limitations

- the udp stream must contain a "time" value field which is used to plot the x-axis.
- for now, the plots are divided by three, two plots on the left side and one big plot on the right side.
- the data is saved in a csv file, being the filename the date and time of the disconnection of the udp stream.
