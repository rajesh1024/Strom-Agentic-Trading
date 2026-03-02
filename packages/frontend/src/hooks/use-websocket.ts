"use client"

import * as React from "react"
import { useQueryClient } from "@tanstack/react-query"
import { useSignalStore, TradingSignal } from "@/store/signal-store"
import { useAgentStore } from "@/store/agent-store"
import { useConfigStore } from "@/store/config-store"
import { toast } from "sonner"

type WSEvent =
    | { type: "portfolio_update", data: any }
    | { type: "signal_received", data: Omit<TradingSignal, "isRead"> }
    | { type: "agent_heartbeat", data: { id: string, timestamp: number } }
    | { type: "agent_status", data: { id: string, status: any } }
    | { type: "order_filled", data: any }

export function useWebSocket() {
    const queryClient = useQueryClient()
    const [isConnected, setIsConnected] = React.useState(false)
    const [isStale, setIsStale] = React.useState(false)

    const wsEndpoint = useConfigStore(state => state.config.wsEndpoint)
    const addSignal = useSignalStore(state => state.addSignal)
    const updateHeartbeat = useAgentStore(state => state.updateHeartbeat)
    const updateAgentStatus = useAgentStore(state => state.updateAgentStatus)

    const processMessage = React.useCallback((event: WSEvent) => {
        setIsStale(false)

        switch (event.type) {
            case "portfolio_update":
                queryClient.invalidateQueries({ queryKey: ["portfolio"] })
                break
            case "signal_received":
                addSignal(event.data)
                toast.info(`New Signal: ${event.data.symbol} ${event.data.action}`, {
                    description: event.data.message
                })
                break
            case "agent_heartbeat":
                updateHeartbeat(event.data.id, event.data.timestamp)
                break
            case "agent_status":
                updateAgentStatus(event.data.id, event.data.status)
                break
            case "order_filled":
                queryClient.invalidateQueries({ queryKey: ["portfolio"] })
                toast.success(`Order Filled`, {
                    description: `${event.data.side} ${event.data.quantity} ${event.data.symbol} @ ${event.data.price}`
                })
                break
        }
    }, [queryClient, addSignal, updateHeartbeat, updateAgentStatus])

    React.useEffect(() => {
        setIsConnected(true)

        const interval = setInterval(() => {
            // Simulate invalidating a query when an event happens
            if (Math.random() > 0.9) {
                queryClient.invalidateQueries({ queryKey: ["market-data"] })
                setIsStale(false)
            } else {
                // for simulation purposes let's just flip stale on very long times but here we just leave it
            }
        }, 5000)

        return () => {
            clearInterval(interval)
            setIsConnected(false)
        }
    }, [wsEndpoint, queryClient])

    return {
        isConnected,
        isStale,
        processMessage,
    }
}
