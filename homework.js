let plain = `139 76 59 3 14 16
220 142 104 84 68 115
159 98 51 121 172 173
223 153 104 152 193 195
253 195 158 112 158 156
228 167 120 93 147 149
232 186 171 144 185 187
209 146 113 88 136 150
148 97 54 93 139 137
223 149 100 250 247 242
234 187 171 19 29 98
228 172 123 129 174 177
251 211 201 102 132 0
140 93 51 201 54 60
223 158 126 32 82 81
225 154 102 61 107 105
217 158 124 88 156 227
215 139 87 11 31 32
149 103 51 145 186 188
157 105 48 104 124 249
210 153 123 254 193 14
198 124 61 135 180 185
254 190 152 100 127 32
234 190 155 163 198 200
240 187 171 127 175 177
`


const extractParts = (line) => {
    let parts = line.split(' ').map(part=>parseInt(part))
    let partA = [parts[0], parts[1], parts[2]]
    let partB = [parts[3], parts[4], parts[5]]
    return [partA, partB]
}

const quicksort = (arr) => {
    if (arr.length <= 1) return arr
    let left = []
    let right = []
    let pivot = arr.shift()

    arr.forEach(item=>item < pivot ? left.push(item) : right.push(item))

    left = quicksort(left)
    right = quicksort(right)

    return left.concat([pivot]).concat(right)

}

let columns = plain.split('\n').filter(k=>k.length).map(k=>extractParts(k))
let grouped = { 'skin':{ children: columns.map(row=>row[0])}, 'nonskin':{children:columns.map(row=>row[1])} }

for (groupKey in grouped){
    let elements = grouped[groupKey].children
    let meanR = elements.reduce((prev, r)=>prev + r[0], 0)
    let meanG = elements.reduce((prev, r)=>prev + r[1], 0)
    let meanB = elements.reduce((prev, r)=>prev + r[2], 0)
    grouped[groupKey]['mean-red'] = meanR / elements.length

    grouped[groupKey]['mean-green'] = meanG / elements.length
    grouped[groupKey]['mean-blue'] = meanB / elements.length

    let distanceMean = Math.abs(grouped[groupKey]['mean-red'] - 145) + Math.abs(grouped[groupKey]['mean-green'] - 140) + Math.abs(grouped[groupKey]['mean-blue'] - 122) 
    grouped[groupKey]['mean-distance'] = distanceMean

    let dotproduct = grouped[groupKey]['mean-red'] * 145 +
                     grouped[groupKey]['mean-green'] * 140 +
                     grouped[groupKey]['mean-blue'] * 122

    let pythagorasA = Math.sqrt(  
        Math.pow(grouped[groupKey]['mean-red'], 2) +
        Math.pow(grouped[groupKey]['mean-green'], 2) +
        Math.pow(grouped[groupKey]['mean-blue'], 2)
    )

    let pythagorasB = Math.sqrt(  
        Math.pow(145, 2) +
        Math.pow(140, 2) +
        Math.pow(122, 2)
    )

    let costheta = dotproduct / (pythagorasA * pythagorasB)
    let cosinedistance = 1 - costheta
    grouped[groupKey]['cosine-distance'] = cosinedistance

    for (let k = 0; k < elements.length; k++) {
        let arr = elements[k]
        let distance = Math.abs(arr[0] - 145) + Math.abs(arr[1] - 140) + Math.abs(arr[2] - 122)
        grouped[groupKey].children[k].push(distance)
    }
}

console.log(grouped)

// justElsSkin = grouped['skin'].children.map(k=>k[3])
// justElsSkin = quicksort(justElsSkin)
// console.log('Skin')
// console.log(justElsSkin, '\n')

// justElsNonSkin = grouped['nonskin'].children.map(k=>k[3])
// justElsNonSkin = quicksort(justElsNonSkin)
// console.log('Non skin')
// console.log(justElsNonSkin, '\n')

// justElsCombined = justElsSkin.concat(justElsNonSkin)
// justElsCombined = quicksort(justElsCombined)
// console.log('combined')
// console.log(justElsCombined)