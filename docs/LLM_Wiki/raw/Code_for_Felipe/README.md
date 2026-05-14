# minOTN/OA Simulator

Hi, I am the **minOTN/OA sequential two-step and three-step simulator**.

## Usage

You can run me with the following command:

```bash
./NBGA 12_node.dat 0 80 0 0 result_25
```

## Important Notes

1.  **Results**:
    *   The optimized OTN final results will be in the `result` file.
    *   The OA optimized results will be in the `OA_GA_result.txt` file.
2.  **Input Files**:
    *   You can create your own input file. Please check the `12_node.dat` file.
    *   **Crucial**: Input files must always have a `.dat` suffix.
3.  **Outputs**:
    *   The `result` file and `OA_GA_result` are not empty currently, so you can have an overview of my output format.
4.  **OA Placement**:
    *   Always double-check that you put the initial OA placement for QoT-aware OTN layer check in `OA_GA_init_v3`.
    *   Always make sure `OA_GA_init.txt` is empty.
5.  **QoT-Awareness**:
    *   I am QoT-aware, meaning that I need to get the OAs as an input.
    *   **Two-step mode**: Provide baseline OA placement.
    *   **Three-step mode**: Provide optimized OA placement from step 1.

---

**Enjoy multi-layer optimization of OTN and WDM layers!**
