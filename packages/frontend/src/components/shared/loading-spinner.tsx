"use client"

import * as React from "react"
import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

export interface LoadingSpinnerProps {
    size?: "sm" | "md" | "lg" | "xl"
    className?: string
    label?: string
}

export function LoadingSpinner({ size = "md", className, label = "Loading..." }: LoadingSpinnerProps) {
    const sizeClasses = {
        sm: "size-4",
        md: "size-6",
        lg: "size-8",
        xl: "size-12",
    }

    return (
        <div className={cn("flex flex-col items-center justify-center gap-2", className)} role="status" aria-label={label}>
            <Loader2 className={cn("animate-spin text-primary", sizeClasses[size])} />
            {label && size !== "sm" && <span className="text-sm font-medium text-muted-foreground">{label}</span>}
            <span className="sr-only">{label}</span>
        </div>
    )
}
