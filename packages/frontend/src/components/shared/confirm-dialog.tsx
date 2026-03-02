"use client"

import * as React from "react"
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"

export interface ConfirmDialogProps {
    trigger?: React.ReactNode
    title: string
    description?: string
    cancelText?: string
    confirmText?: string
    onConfirm: () => void
    onCancel?: () => void
    variant?: "default" | "destructive"
    isOpen?: boolean
    onOpenChange?: (open: boolean) => void
}

export function ConfirmDialog({
    trigger,
    title,
    description,
    cancelText = "Cancel",
    confirmText = "Confirm",
    onConfirm,
    onCancel,
    variant = "default",
    isOpen,
    onOpenChange,
}: ConfirmDialogProps) {
    return (
        <AlertDialog open={isOpen} onOpenChange={onOpenChange}>
            {trigger && (
                <AlertDialogTrigger asChild>
                    {trigger}
                </AlertDialogTrigger>
            )}
            <AlertDialogContent className="bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
                <AlertDialogHeader>
                    <AlertDialogTitle className="text-xl font-bold tracking-tight">{title}</AlertDialogTitle>
                    {description && (
                        <AlertDialogDescription className="text-muted-foreground">
                            {description}
                        </AlertDialogDescription>
                    )}
                </AlertDialogHeader>
                <AlertDialogFooter className="gap-2">
                    <AlertDialogCancel onClick={onCancel} className="bg-secondary/50 hover:bg-secondary">
                        {cancelText}
                    </AlertDialogCancel>
                    <AlertDialogAction
                        onClick={onConfirm}
                        className={variant === "destructive" ? "bg-destructive text-destructive-foreground hover:bg-destructive/90" : "bg-primary text-primary-foreground hover:bg-primary/90"}
                    >
                        {confirmText}
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    )
}
