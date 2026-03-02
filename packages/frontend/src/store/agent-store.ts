import { create } from "zustand"

export type AgentStatus = "running" | "stopped" | "error" | "paused"

export interface TradingAgent {
    id: string
    name: string
    type: "equity" | "crypto" | "universal"
    status: AgentStatus
    lastHeartbeat: number
    activeTrades: number
    winRate: number
}

interface AgentState {
    agents: Record<string, TradingAgent>

    // Actions
    setAgent: (agent: TradingAgent) => void
    updateAgentStatus: (id: string, status: AgentStatus) => void
    updateHeartbeat: (id: string, timestamp: number) => void
    removeAgent: (id: string) => void

    // Selectors
    getRunningAgents: () => TradingAgent[]
    getStaleAgents: (thresholdMs?: number) => TradingAgent[]
}

export const useAgentStore = create<AgentState>((set, get) => ({
    agents: {},

    setAgent: (agent) => set((state) => ({
        agents: { ...state.agents, [agent.id]: agent }
    })),

    updateAgentStatus: (id, status) => set((state) => {
        const agent = state.agents[id]
        if (!agent) return state

        return {
            agents: { ...state.agents, [id]: { ...agent, status } }
        }
    }),

    updateHeartbeat: (id, timestamp) => set((state) => {
        const agent = state.agents[id]
        if (!agent) return state

        return {
            agents: { ...state.agents, [id]: { ...agent, lastHeartbeat: timestamp } }
        }
    }),

    removeAgent: (id) => set((state) => {
        const newAgents = { ...state.agents }
        delete newAgents[id]
        return { agents: newAgents }
    }),

    getRunningAgents: () => Object.values(get().agents).filter(a => a.status === "running"),

    // Default threshold is 30 seconds (30000 ms)
    getStaleAgents: (thresholdMs = 30000) => {
        const now = Date.now()
        return Object.values(get().agents).filter(a =>
            a.status === "running" && (now - a.lastHeartbeat) > thresholdMs
        )
    }
}))
