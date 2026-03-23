-- KEYS[1] = cart:{user_id}:{session_id}
-- KEYS[2] = cart_seats:{user_id}:{session_id}
-- KEYS[3..N] = seat:{session_id}:{seat_id}

-- ARGV[1] = ttl
-- ARGV[2] = user_id
-- ARGV[3] = session_id
-- ARGV[4..N] = seat_ids

local RESULT = {
    OK            = 1,
    CART_EXISTS   = 2,
    SEAT_CONFLICT = 3
}

local cart_key = KEYS[1]
local cart_seats_key = KEYS[2]
local ttl = tonumber(ARGV[1])
local user_id = ARGV[2]
local session_id = ARGV[3]

local lock_keys = {}
local seat_ids = {}
for i = 3, #KEYS do
    lock_keys[#lock_keys + 1] = KEYS[i]
    seat_ids[#seat_ids + 1] = ARGV[i + 1]
end

-- Verifica carrinho ativo
if redis.call("EXISTS", cart_key) == 1 then
    return RESULT.CART_EXISTS
end

-- Verifica conflitos
local locks = redis.call("MGET", unpack(lock_keys))
for _, lock in ipairs(locks) do
    if lock then
        return RESULT.SEAT_CONFLICT
    end
end

-- Cria estrutura atomicamente
redis.call("SET", cart_key, "1", "EX", ttl)
redis.call("DEL", cart_seats_key)
redis.call("SADD", cart_seats_key, unpack(seat_ids))

-- Define locks
local mset_args = {}
for i, lock_key in ipairs(lock_keys) do
    mset_args[#mset_args + 1] = lock_key
    mset_args[#mset_args + 1] = user_id
end
redis.call("MSET", unpack(mset_args))

return RESULT.OK
