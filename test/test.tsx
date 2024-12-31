'use client'

import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/app/components/ui/dialog'
import { useLoginFromEventSource } from '@/tools/login-helper'
import { Card, CardBody, CardFooter, CardHeader, Chip, Divider } from '@nextui-org/react'
import { CircleCheck } from 'lucide-react'
import { useState } from 'react'

export default function WelcomeToCodeGPT({ open }: { open: boolean }) {
  const [isOpen, setOpen] = useState(open)
  const { loginFromEventSource } = useLoginFromEventSource()
  const cards = [
    {
      title: 'Plus Teams',
      items: [
        '$19.99 consumption credits',
        'Unlimited Custom AI Agents',
        '100 daily chat interactions per seat'
      ],
      price: 'Start for $18.32 / mo',
      onClick: async () => {
        void loginFromEventSource({
          type: 'signup',
          next: '/account/subscription',
          callback: () => {
            setOpen(false)
          }
        })
      }
    },
    {
      title: 'Plus Free',
      items: [
        'Access to Azure GPT4/3.5 Turbo / Bedrock AI',
        '3 AI Marketplace Agents',
        '1 Custom AI Agent',
        'Up to 8 daily chat interactions'
      ],
      price: 'Start for $0',
      onClick: () => {
        void loginFromEventSource({
          type: 'signup',
          callback: () => {
            setOpen(false)
          }
        })
      }
    },
    {
      title: 'Use your own LLM Provider',
      items: [
        'Api key required',
        'Provider and models installation required',
        'Interaction cost..',
        'No access to CodeGPT AI Agents'
      ],
      price: '3rd party LLM costs...',
      onClick: () => {
        setOpen(false)
      }
    }
  ]
  return (
    <Dialog open={isOpen} onOpenChange={() => setOpen(false)}>
      <DialogContent className='top-[1rem] max-w-xl select-none border border-purple-400/60 bg-black  p-0'>
        <div className='bg-custom-radial flex flex-col gap-4 rounded-lg p-6'>
          <DialogHeader>
            <div className='space-y-1 text-center'>
              <h1 className='text-2xl font-bold text-white'>Welcome to CODEGPT</h1>
              <p className='text-xl text-gray-200'>How would you like to start?</p>
            </div>
          </DialogHeader>
          <div className='space-y-4'>
            {cards.map((card, index) => (
              <Card
                className='w-full cursor-pointer border  border-purple-300 bg-purple-900 hover:border-purple-400 hover:bg-purple-800'
                key={card.title}
                isPressable
                onPress={() => {
                  card.onClick()
                }}
              >
                <CardHeader className='px-5'>
                  <div className='flex w-full items-center justify-between'>
                    <DialogTitle className='text-xl text-white'>{card.title}</DialogTitle>
                    {index === 0 && (
                      <Chip className='border border-purple-400 bg-purple-400/60' size='sm'>
                        Popular
                      </Chip>
                    )}
                  </div>
                </CardHeader>
                <CardBody>
                  <div className='space-y-2 px-2'>
                    {card.items.map((item, itemIndex) => (
                      <div className='flex items-center gap-2' key={`${item}-${itemIndex}`}>
                        <CircleCheck className='size-5' />
                        <p className='text-sm text-gray-200'>{item}</p>
                      </div>
                    ))}
                  </div>
                </CardBody>
                <Divider />
                <CardFooter>
                  <span className='ml-auto text-sm text-foreground underline underline-offset-4'>
                    {card.price}
                  </span>
                </CardFooter>
              </Card>
            ))}
          </div>
          <DialogFooter>
            <div className='mx-auto space-y-1 text-center'>
              <p className='text-lg text-white'>Not sure yet?</p>
              <p className='underline underline-offset-4 hover:cursor-pointer'>
                Try 4 interactions for free – No account needed
              </p>
            </div>
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>
  )