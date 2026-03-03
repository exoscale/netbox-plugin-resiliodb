class CPUData:
    """
    Stores CPU specifications and provides lookup functionality
    """

    # Default values if CPU not found
    DEFAULT_LITHO_NM = 14
    DEFAULT_DIE_SURFACE_MM2 = 126

    # CPU specifications database
    CPU_SPECS = {
        "AMD EPYC 7413": {"litho_nm": 7, "die_surface_mm2": 324},
        "Intel(R) Xeon(R) CPU  E5540": {"litho_nm": 45, "die_surface_mm2": 263},
        "Intel(R) Xeon(R) CPU  E5620": {"litho_nm": 32, "die_surface_mm2": 239},
        "Intel(R) Xeon(R) CPU  X5650": {"litho_nm": 32, "die_surface_mm2": 240},
        "Intel(R) Xeon(R) CPU D-1518": {"litho_nm": 14, "die_surface_mm2": 246},
        "Intel(R) Xeon(R) CPU D-1537": {"litho_nm": 14, "die_surface_mm2": 246},
        "Intel(R) Xeon(R) CPU E3-1230 v6": {"litho_nm": 14, "die_surface_mm2": 126},
        "Intel(R) Xeon(R) CPU E5-2650 v2": {"litho_nm": 32, "die_surface_mm2": 435},
        "Intel(R) Xeon(R) CPU E5-2660": {"litho_nm": 32, "die_surface_mm2": 435},
        "Intel(R) Xeon(R) CPU E5-2660 v2": {"litho_nm": 22, "die_surface_mm2": 160},
        "Intel(R) Xeon(R) CPU E5-2670 v2": {"litho_nm": 22, "die_surface_mm2": 160},
        "Intel(R) Xeon(R) CPU E5-2676 v3": {"litho_nm": 22, "die_surface_mm2": 356},
        "Intel(R) Xeon(R) CPU E5-2680 v4": {"litho_nm": 14, "die_surface_mm2": 306},
        "Intel(R) Xeon(R) D-2183IT": {"litho_nm": 14, "die_surface_mm2": 484},
        "Intel(R) Xeon(R) Gold 5120": {"litho_nm": 14, "die_surface_mm2": 484},
        "Intel(R) Xeon(R) Gold 6148": {"litho_nm": 14, "die_surface_mm2": 698},
    }

    @classmethod
    def get_cpu_specs(cls, cpu_name):
        """
        Look up CPU specifications by name.
        Returns dict with litho_nm and die_surface_mm2.
        Falls back to default values if CPU not found.
        """
        # Try to find an exact match
        if cpu_name in cls.CPU_SPECS:
            return cls.CPU_SPECS[cpu_name]

        # Try to find a partial match
        for known_cpu, specs in cls.CPU_SPECS.items():
            if known_cpu in cpu_name or cpu_name in known_cpu:
                return specs

        # Return default values if no match found
        return {
            "litho_nm": cls.DEFAULT_LITHO_NM,
            "die_surface_mm2": cls.DEFAULT_DIE_SURFACE_MM2,
        }
