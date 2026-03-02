import { create } from "zustand"
import { persist } from "zustand/middleware"

export type AssetType = "equity" | "crypto"

export interface Transaction {
    id: string
    symbol: string
    type: AssetType
    side: "buy" | "sell"
    price: number
    quantity: number
    timestamp: number
    status: "filled" | "pending" | "failed"
}

export interface Position {
    symbol: string
    type: AssetType
    avgPrice: number
    quantity: number
    currentPrice: number
    pnl: number
    pnlPercentage: number
}

interface PortfolioState {
    positions: Position[]
    balance: {
        total: number
        equity: number
        crypto: number
        cash: number
    }
    history: Transaction[]

    // Actions
    setPositions: (positions: Position[]) => void
    updateBalance: (balance: Partial<PortfolioState["balance"]>) => void
    addTransaction: (transaction: Transaction) => void

    // Selectors
    getEquityPositions: () => Position[]
    getCryptoPositions: () => Position[]
}

export const usePortfolioStore = create<PortfolioState>()(
    persist(
        (set, get) => ({
            positions: [],
            balance: {
                total: 0,
                equity: 0,
                crypto: 0,
                cash: 0,
            },
            history: [],

            setPositions: (positions) => set({ positions }),
            updateBalance: (balance) => set((state) => ({
                balance: { ...state.balance, ...balance }
            })),
            addTransaction: (transaction) => set((state) => ({
                history: [transaction, ...state.history].slice(0, 100)
            })),

            getEquityPositions: () => get().positions.filter((p) => p.type === "equity"),
            getCryptoPositions: () => get().positions.filter((p) => p.type === "crypto"),
        }),
        {
            name: "strom-portfolio-storage",
        }
    )
)
