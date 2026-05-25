"use client";

import { Dialog as DialogPrimitive } from "@base-ui/react/dialog";
import { cva, type VariantProps } from "class-variance-authority";
import { X } from "lucide-react";
import * as React from "react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const Sheet = DialogPrimitive.Root;
const SheetTrigger = DialogPrimitive.Trigger;
const SheetClose = DialogPrimitive.Close;
const SheetPortal = DialogPrimitive.Portal;

const SheetOverlay = ({ className, ...props }: DialogPrimitive.Backdrop.Props) => (
  <DialogPrimitive.Backdrop
    className={cn(
      "fixed inset-0 z-50 bg-black/80 data-open:animate-in data-open:fade-in-0 data-closed:animate-out data-closed:fade-out-0",
      className
    )}
    {...props}
  />
);

const sheetVariants = cva(
  "fixed z-50 gap-4 bg-background p-6 shadow-lg transition ease-in-out data-closed:duration-300 data-open:duration-500 data-open:animate-in data-closed:animate-out",
  {
    variants: {
      side: {
        left: "inset-y-0 left-0 h-full w-3/4 border-r data-closed:slide-out-to-left data-open:slide-in-from-left sm:max-w-sm",
      },
    },
    defaultVariants: {
      side: "left",
    },
  }
);

interface SheetContentProps
  extends VariantProps<typeof sheetVariants> {
  showClose?: boolean;
  className?: string;
  children?: React.ReactNode;
}

const SheetContent = ({
  className,
  side,
  children,
  showClose = true,
}: SheetContentProps) => (
  <SheetPortal>
    <SheetOverlay />
    <DialogPrimitive.Popup
      className={cn(sheetVariants({ side }), className)}
    >
      {showClose && (
        <DialogPrimitive.Close
          className="absolute right-4 top-4 rounded-sm opacity-70 transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring disabled:pointer-events-none data-open:bg-secondary"
          render={<Button variant="ghost" size="icon" />}
        >
          <X className="h-4 w-4" />
          <span className="sr-only">Tutup</span>
        </DialogPrimitive.Close>
      )}
      {children}
    </DialogPrimitive.Popup>
  </SheetPortal>
);

export {
  Sheet,
  SheetClose,
  SheetContent,
  SheetOverlay,
  SheetPortal,
  SheetTrigger,
};
