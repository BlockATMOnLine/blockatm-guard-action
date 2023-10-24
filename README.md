# BlockATM-Guard-Action

## 简介：

用于将 [BlockATM-Guard](https://github.com/BlockATMOnLine/blockatm-guard) 项目打包成桌面端应用程序

## 搭建環境

### 拉取BlockATM-Guard仓库

```
git clone https://github.com/BlockATMOnLine/blockatm-guard.git
```

### Python環境

python > 3.9

```
# windows
python3 -m pip install -r blockatm-guard/requirements_windows.txt

# mac
python3 -m pip install -r blockatm-guard/requirements_mac.txt
```

### 打包

```
python3 script/build.py
```

