"use client"

import * as React from "react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

export type AssetClass =
    | "equity"
    | "crypto"
    | "fom"
    | "commodity"
    | "currency"
    | "index"
    | (string & {})

export interface AssetClassBadgeProps {
    assetClass: AssetClass
    className?: string
}

const assetClassStyles: Record<string, string> = {
    equity: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20 hover:bg-emerald-500/20",
    crypto: "bg-purple-500/10 text-purple-500 border-purple-500/20 hover:bg-purple-500/20",
    fom: "bg-blue-500/10 text-blue-500 border-blue-500/20 hover:bg-blue-500/20",
    commodity: "bg-orange-500/10 text-orange-500 border-orange-500/20 hover:bg-orange-500/20",
    currency: "bg-cyan-500/10 text-cyan-500 border-cyan-500/20 hover:bg-cyan-500/20",
    index: "bg-slate-500/10 text-slate-500 border-slate-500/20 hover:bg-slate-500/20",
}

export function AssetClassBadge({ assetClass, className }: AssetClassBadgeProps) {
    const normalizedClass = assetClass.toLowerCase()
    const customStyles = assetClassStyles[normalizedClass] || assetClassStyles.index

    return (
        <Badge
            variant="outline"
            className={cn("px-2.5 py-0.5 font-bold uppercase tracking-wider text-[10px]", customStyles, className)}
            aria-label={`Asset class: ${assetClass}`}
        >
            {assetClass}
        </Badge>
    )
}
