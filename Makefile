export PYTHONPATH := ${PYTHONPATH}:./create_llama/backend
export CREATE_LLAMA_VERSION=0.1.7
export NEXT_PUBLIC_API_URL=/api/chat


run:
	poetry run uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# dev:
# # Start the backend and frontend servers
# # Kill both servers if a stop signal is received
# 	@export ENVIRONMENT=dev; \
# 	trap 'kill 0' SIGINT; \
# 	poetry run python main.py & \
# 	# npm run dev --prefix ./create_llama/frontend & \
# 	# sleep 1; \
# 	# npm run dev --prefix ./admin & \
# 	wait

dev:
	set ENVIRONMENT=dev && \
	start poetry run python main.py
