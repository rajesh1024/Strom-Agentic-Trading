import { create } from "zustand"

export type SignalLevel = "info" | "warning" | "critical"

export interface TradingSignal {
    id: string
    symbol: string
    action: "buy" | "sell" | "hold"
    level: SignalLevel
    message: string
    confidence: number
    timestamp: number
    isRead: boolean
}

interface SignalState {
    signals: TradingSignal[]
    unreadCount: number

    // Actions
    addSignal: (signal: Omit<TradingSignal, "isRead">) => void
    markAsRead: (id: string) => void
    markAllAsRead: () => void
    clearSignals: () => void
}

export const useSignalStore = create<SignalState>((set) => ({
    signals: [],
    unreadCount: 0,

    addSignal: (signal) => set((state) => {
        const newSignal = { ...signal, isRead: false }
        const newSignals = [newSignal, ...state.signals].slice(0, 100) // Keep last 100
        return {
            signals: newSignals,
            unreadCount: state.unreadCount + 1
        }
    }),

    markAsRead: (id) => set((state) => {
        const selected = state.signals.find(s => s.id === id)
        if (!selected || selected.isRead) return state

        return {
            signals: state.signals.map(s => s.id === id ? { ...s, isRead: true } : s),
            unreadCount: Math.max(0, state.unreadCount - 1)
        }
    }),

    markAllAsRead: () => set((state) => ({
        signals: state.signals.map(s => ({ ...s, isRead: true })),
        unreadCount: 0
    })),

    clearSignals: () => set({ signals: [], unreadCount: 0 })
}))
