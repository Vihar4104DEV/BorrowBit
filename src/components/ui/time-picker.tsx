import * as React from "react"
import { Clock } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface TimePickerProps {
  time?: string
  onTimeChange?: (time: string) => void
  placeholder?: string
  disabled?: boolean
  className?: string
}

export function TimePicker({
  time,
  onTimeChange,
  placeholder = "Pick a time",
  disabled = false,
  className
}: TimePickerProps) {
  const [selectedTime, setSelectedTime] = React.useState(time || "")

  const handleTimeChange = (newTime: string) => {
    setSelectedTime(newTime)
    onTimeChange?.(newTime)
  }

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant={"outline"}
          className={cn(
            "w-full justify-start text-left font-normal",
            !selectedTime && "text-muted-foreground",
            className
          )}
          disabled={disabled}
        >
          <Clock className="mr-2 h-4 w-4" />
          {selectedTime ? selectedTime : <span>{placeholder}</span>}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-4" align="start">
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="time-input">Select Time</Label>
            <Input
              id="time-input"
              type="time"
              value={selectedTime}
              onChange={(e) => handleTimeChange(e.target.value)}
              className="w-full"
            />
          </div>
          <div className="grid grid-cols-4 gap-2">
            {[
              "09:00", "10:00", "11:00", "12:00",
              "13:00", "14:00", "15:00", "16:00",
              "17:00", "18:00", "19:00", "20:00"
            ].map((t) => (
              <Button
                key={t}
                variant={selectedTime === t ? "default" : "outline"}
                size="sm"
                onClick={() => handleTimeChange(t)}
                className="text-xs"
              >
                {t}
              </Button>
            ))}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  )
}
