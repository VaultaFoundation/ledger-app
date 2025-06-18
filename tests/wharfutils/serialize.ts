import { Serializer, ABI, Bytes } from '@wharfkit/antelope'
import * as fs from 'fs'
import * as path from 'path'

// Parse CLI arguments
const [,, actionDataPathArg, abiPathArg, formatArg, typeArg] = process.argv

if (!actionDataPathArg) {
    console.error('Usage: ts-node serialize.ts <actionDataPath> [abiPath=./abi.json] [format=python-byte-string] [type=transaction]')
    process.exit(1)
}

const actionDataPath = actionDataPathArg
const abiPath = abiPathArg || './transaction.abi.json'
const format = formatArg || 'python-byte-string'
const abiType = typeArg || 'transaction'

// Load files
const transactionData = JSON.parse(fs.readFileSync(path.resolve(actionDataPath), 'utf-8'))
const abiJson = JSON.parse(fs.readFileSync(path.resolve(abiPath), 'utf-8'))

// Initialize ABI
const abi = ABI.from(abiJson)

// backward compatibility with older test json 
// older json includes chain-id and nested transaction object
// will return simple objects as well
function extractTransactionOrAll(obj: any): any {
    if (obj && typeof obj === 'object' && 'transaction' in obj) {
        return obj.transaction
    }
    return obj
}

// Encode by ABI for given type, type defaults to 'transaction'
const encoded = Serializer.encode({ object: extractTransactionOrAll(transactionData), 
  abi: abi, 
  type: abiType })

// easier compat with python 
function toPythonByteString(bytes: Bytes): string {
  return "b'" + Array.from(bytes.array)
    .map(b => `\\x${b.toString(16).padStart(2, '0')}`)
    .join('') + "'"
}

switch (format) {
    case 'python-byte-string':
        console.log(toPythonByteString(encoded))
        break
    case 'hex':
        console.log(String(encoded))
        break
    case 'utf8-string':
        console.log(encoded.utf8String)
        break
    default:
        console.error(`Unknown format: ${format}`)
        process.exit(1)
}
