import React, { useState } from "react";
import * as SwitchPrimitive from "@radix-ui/react-switch";
import { cn } from "./lib/utils";

// Root component for the switch
const Switch = React.forwardRef<
  React.ElementRef<typeof SwitchPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof SwitchPrimitive.Root> & { onCheckedChange?: (checked: boolean) => void }
>(({ className, onCheckedChange, ...props }, ref) => (
  <SwitchPrimitive.Root
    ref={ref}
    className={cn(
      "relative inline-flex h-4 w-10 items-center rounded-full",
      "bg-gray-200 data-[state=checked]:bg-gray-500",
      className
    )}
    onCheckedChange={onCheckedChange}
    {...props}
  />
));
Switch.displayName = SwitchPrimitive.Root.displayName;

// Thumb component for the switch
const SwitchThumb = React.forwardRef<
  React.ElementRef<typeof SwitchPrimitive.Thumb>,
  React.ComponentPropsWithoutRef<typeof SwitchPrimitive.Thumb>
>(({ className, ...props }, ref) => (
  <SwitchPrimitive.Thumb
    ref={ref}
    className={cn(
      "inline-block h-3 w-3 transform rounded-full bg-white transition",
      "translate-x-1 data-[state=checked]:translate-x-6",
      className
    )}
    {...props}
  />
));
SwitchThumb.displayName = SwitchPrimitive.Thumb.displayName;

// Label component for the switch
const SwitchLabel = React.forwardRef<
  React.ElementRef<"label">,
  React.ComponentPropsWithoutRef<"label">
>(({ className, children, ...props }, ref) => (
  <label
    ref={ref}
    className={cn("text-sm font-medium text-gray-900", className)}
    {...props}
  >
    {children}
  </label>
));
SwitchLabel.displayName = "SwitchLabel";

export {
  Switch,
  SwitchThumb,
  SwitchLabel,
};
