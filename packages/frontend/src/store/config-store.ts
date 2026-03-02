import { create } from "zustand"
import { persist } from "zustand/middleware"

export type TradingMode = "advisory" | "semi-auto"
export type RiskLevel = "low" | "medium" | "high"

export interface SystemConfig {
    mode: TradingMode
    riskTolerance: RiskLevel
    maxDrawdownPct: number
    autoConfirmSignals: boolean
    wsEndpoint: string
    isKillSwitchEngaged: boolean
}

interface ConfigState {
    config: SystemConfig

    // Actions
    updateConfig: (updates: Partial<SystemConfig>) => void
    toggleMode: () => void
    engageKillSwitch: () => void
    disengageKillSwitch: () => void
}

const DEFAULT_CONFIG: SystemConfig = {
    mode: "advisory",
    riskTolerance: "low",
    maxDrawdownPct: 5.0,
    autoConfirmSignals: false,
    wsEndpoint: "ws://localhost:8000/ws",
    isKillSwitchEngaged: false,
}

export const useConfigStore = create<ConfigState>()(
    persist(
        (set) => ({
            config: DEFAULT_CONFIG,

            updateConfig: (updates) => set((state) => ({
                config: { ...state.config, ...updates }
            })),

            toggleMode: () => set((state) => ({
                config: {
                    ...state.config,
                    mode: state.config.mode === "advisory" ? "semi-auto" : "advisory",
                    autoConfirmSignals: state.config.mode === "advisory", // Will become true if switching to semi-auto
                }
            })),

            engageKillSwitch: () => set((state) => ({
                config: { ...state.config, isKillSwitchEngaged: true, mode: "advisory" }
            })),

            disengageKillSwitch: () => set((state) => ({
                config: { ...state.config, isKillSwitchEngaged: false }
            })),
        }),
        {
            name: "strom-config-storage",
        }
    )
)
