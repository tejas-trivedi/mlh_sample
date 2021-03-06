
class MyCartListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request,*args,**kwargs):
        try:
            cart = Cart.objects.filter(user=request.user)
            print(cart)
            context = {
                "request": request,
            }

            my_cart_serializer = CartSerializer(cart, many=True, context=context)
            response = my_cart_serializer.data

            cart_item = CartItem.objects.filter(cart=cart[0])

            my_cart = Cart()
            total_cart_amount = 0
            cart_item_serializer = CartItemSerializer(cart_item, many=True, context=context)
            response_temp = cart_item_serializer.data

            for res in range(0, len(response_temp)):
                total_cart_amount += Decimal(response_temp[res]['line_item_total'])

            my_cart.total = total_cart_amount

            data = {
                "amount": my_cart.total
            }
            print(data)

            amount_update_serializer = CartSerializer(cart, data=data, partial=True)#, data=data, partial=True)
            #print(amount_update_serializer.data[0]['total'])
            if amount_update_serializer.is_valid():
                print("True")

            return Response(response, status=status.HTTP_200_OK)

        except Cart.DoesNotExist:
            errors = {"message":["No cart found"]}
            return Response(errors, status=status.HTTP_404_NOT_FOUND)



class CartItemsListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request,*args,**kwargs):
        try:
            cart = Cart.objects.filter(user=request.user)

            cart1 = cart.values_list('items', flat=True)
            print(len(cart1))
            cart_item = CartItem.objects.filter(cart=cart[0])
            #print(cart_item)

            my_cart_courses_list = []

            for i in range(0, len(cart1)):
                course = AllCourses.objects.filter(id=str(cart1[i]))
                all_serializer = AllCoursesSerializer(course, many=True,)
                #print(all_serializer.data)
                data_tba = all_serializer.data
                my_cart_courses_list.append(data_tba)

            print(my_cart_courses_list)
            response = my_cart_courses_list

            context = {
                "request": request,
            }

            return Response(response, status=status.HTTP_200_OK)

        except Cart.DoesNotExist:
            errors = {"message":["No cart found"]}
            return Response(errors, status=status.HTTP_404_NOT_FOUND)



class CreateMyCart(APIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        data = {
            "user": request.user,
        }
        serializer = CartSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "message": "Your cart is ready"
            }
            return Response(
                response,
                status = status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateMyCart(APIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        cart = Cart.objects.filter(user=request.user)
        context = {
                "request": request,
            }
        cart_item = CartItem.objects.filter(cart=cart[0])

        total_cart_amount = 0
        cart_item_serializer = CartItemSerializer(cart_item, many=True, context=context)
        response_temp = cart_item_serializer.data

        for res in range(0, len(response_temp)):
            total_cart_amount += Decimal(response_temp[res]['line_item_total'])

        print(total_cart_amount)

        data = {
            "total": total_cart_amount,
        }
        serializer = CartSerializer(cart[0], data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                "message": "Your cart is updated"
            }
            return Response(
                response,
                status = status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )



class AddItemToCart(APIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        my_cart = Cart.objects.filter(user=request.user)

        cart = my_cart[0]
        item = request.data.get("item")
        quantity = request.data.get("quantity")

        item_course = AllCourses.objects.filter(id=item)
        item_price = Decimal(list(item_course.values_list('discounted_price', flat=True))[0])
        print(item_price)

        data = {
            "cart": str(cart),
            "item": item,
            "quantity": quantity,
            "line_item_total": item_price*int(quantity),
        }

        serializer = CartItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "message": "Item has been added to the cart"
            }

            return Response(
                response,
                status = status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )