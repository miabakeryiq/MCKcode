# Health
curl http://localhost:3000/health

# Get prices
curl http://localhost:3000/screens/mckenzie-main/prices

# Merge prices
curl -X POST http://localhost:3000/screens/mckenzie-main/prices \
  -H "Content-Type: application/json" \
  -d '{"beef_liver_s": 9}'

# Replace all prices
curl -X PUT http://localhost:3000/screens/mckenzie-main/prices \
  -H "Content-Type: application/json" \
  -d '{"beef_liver_s": 8, "beef_liver_m": 13}'
