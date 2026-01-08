# Reversi (C++ core + Python GUI)

This project implements Reversi/Othello with:
- C++ core (OOP) compiled as a DLL
- Python GUI using pygame
- Python calls the C API via ctypes

## Build (Windows)

Prerequisites:
- CMake 3.20+
- MSVC Build Tools (Visual Studio or Build Tools)
- Python 3.10+

Steps:
1. Configure and build the DLL

```powershell
cd C:\\Users\\User\\Desktop\\cursor-oop
mkdir build
cd build
cmake -G "Visual Studio 17 2022" ..
cmake --build . --config Release
```

The DLL will be at something like:
- `build/Release/reversi_core.dll`

Copy it next to Python files:

```powershell
copy .\\Release\\reversi_core.dll ..\\python\\reversi_core.dll
```

2. Install Python dependencies and run

```powershell
pip install -r ..\\requirements.txt
python ..\\python\\main.py
```

## Project Structure
- `cpp/include` C++ headers (`Board.hpp`, `Game.hpp`, `api.h`)
- `cpp/src` C++ sources and C API wrapper
- `python/` Python ctypes wrapper and pygame GUI

## Controls
- Left click to place a disc on a valid square
- Small green dots indicate valid moves

## Notes
- Two-player local (pass-and-play). AI is not included but can be added later.
- The C API exposes opaque game handles for safe interop.


# opp_cursova
